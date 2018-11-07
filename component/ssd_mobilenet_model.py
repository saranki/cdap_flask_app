import csv
import time

import collections
import os
import numpy as np
import tensorflow as tf
from PIL import Image
from matplotlib import pyplot as plt

# from component.signboard import journey_location_csv, db_data_csv
from object_detection.utils import ops as utils_ops
from object_detection.utils.visualization_utils import visualize_boxes_and_labels_on_image_array

if tf.__version__ < '1.4.0':
    raise ImportError('Please upgrade your TensorFlow installation to v1.4.* or later!')

# Object detection imports
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Variables
# Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `PATH_TO_CKPT`
# to point to a new .pb file.
MODEL_NAME = 'pedestrian_crossing_graph'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('pedestrian_crossing_graph', 'pedestrian_crossing_label_map.pbtxt')

NUM_CLASSES = 1

journey_location_csv = 'static/video/journey_csv/'
db_data_csv = 'component/db/'

# Load a (frozen) Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# Helper code for image loading to numpy array
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


# Detection
PATH_TO_TEST_IMAGES_DIR = 'test_images'
TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 11)]

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)


def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.Session() as sess:
            # Get handles to input and output tensors
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                        tensor_name)
            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size
                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image.shape[0], image.shape[1])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            print('Pedestrian crossing detection inference time:')
            start_time = time.time()

            # Run inference
            output_dict = sess.run(tensor_dict, feed_dict={image_tensor: np.expand_dims(image, 0)})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]

            output_dict['inference_time'] = time.time() - start_time

            print('Iteration %d: %.3f sec' % (1, time.time() - start_time))

    return output_dict


def execute_in_order_pedestrian(images_dir, total_frame_count, journey_name):
    inference_dir = [os.path.join(images_dir, '{}_image_{}.jpg'.format(journey_name, i)) for i in
                     range(1, total_frame_count)]

    with open(db_data_csv + journey_name + '.csv', 'w') as f:
        with detection_graph.as_default():
            with tf.Session(graph=detection_graph) as sess:
                image_id = 1
                for image_path in inference_dir:
                    image = Image.open(image_path)

                    # the array based representation of the image will be used later in order to prepare the
                    # result image with boxes and labels on it.
                    image_np = load_image_into_numpy_array(image)

                    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                    image_np_expanded = np.expand_dims(image_np, axis=0)
                    # image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

                    # Actual detection.
                    output_dict = run_inference_for_single_image(image_np, detection_graph)

                    description = visualize_boxes_and_labels_on_image_array(
                        image_np,
                        output_dict['detection_boxes'],
                        output_dict['detection_classes'],
                        output_dict['detection_scores'],
                        category_index,
                        instance_masks=output_dict.get('detection_masks'),
                        use_normalized_coordinates=True,
                        line_thickness=8)

                    with open(journey_location_csv + journey_name + '.csv') as a:
                        print('opened')
                        reader = csv.reader(a)
                        for row in reader:

                            search_fid = str(row).strip('[]').split(',')[0].strip("' '")

                            if search_fid == str(image_id) and description[2] >= 65 and description[1] is not None:
                                latitude = str(row).strip('[]').split(',')[1].strip("' '")
                                longitude = str(row).strip('[]').split(',')[2].strip("' '")
                                print("search id", search_fid)
                                f.write('{},{},{},{},{}\n'.format(image_id, latitude, longitude, description[1],
                                                                  description[2]))
                                print("ID", image_id)
                                break

                    image_id = image_id + 1


def display_single_image_details_crossing(image_path):
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            image = Image.open(image_path)
            image_np = load_image_into_numpy_array(image)
            image_np_expanded = np.expand_dims(image_np, axis=0)
            output_dict = run_inference_for_single_image(image_np, detection_graph)
            description = visualize_boxes_and_labels_on_image_array(
                image_np,
                output_dict['detection_boxes'],
                output_dict['detection_classes'],
                output_dict['detection_scores'],
                category_index,
                instance_masks=output_dict.get('detection_masks'),
                use_normalized_coordinates=True,
                line_thickness=8)
            plt.figure(figsize=IMAGE_SIZE)
            plt.imshow(image_np)
            description.append(output_dict['inference_time'])

    return description
