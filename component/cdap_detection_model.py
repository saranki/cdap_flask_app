import csv
import math
import os
import xml.etree.ElementTree as et
from decimal import *

import cv2
import numpy as np
from flask import request
from tqdm import tqdm
from werkzeug.utils import secure_filename

import sys
import subprocess

# from component.model_trainer import model
from component.faster_rcnn_model import execute_in_order
# from component.processor import IMG_SIZE
from component.faster_rcnn_model import execute_in_order, display_single_image_details
from component.ssd_mobilenet_model import execute_in_order_pedestrian, display_single_image_details_crossing

# from component.processor import IMG_SIZE

# Variable declaration
root_path = 'static/'
xml_file_name = 'static/video/xml/'
journey_location_csv = 'static/video/journey_csv/'
db_data_csv = 'component/db/'

getcontext().prec = 16


# model = 'model.ckpt-70393.data-00000-of-00001'

# --------------------------------------------------------------------------------------------------------------------#

# Method - 1: Split the journey video into images for further prediction processing.

def split_video_to_image():
    global video_name
    global total_frame_count
    global optimized_frame_count
    file = request.files['multipartFile']
    filename = secure_filename(file.filename)
    video_name = filename.split('.')[0]
    # new_path = os.path.abspath(filename)
    video_cap = cv2.VideoCapture(root_path + 'video/' + filename)
    # print("PATH", static/video/journey_video_0001.mp4)
    frame_rate = video_cap.get(cv2.CAP_PROP_FPS)
    # print('frame_rate:------------------>', frame_rate)
    total_frame_count = video_cap.get(cv2.cv2.CAP_PROP_FRAME_COUNT)
    optimized_frame_count = math.ceil(total_frame_count / frame_rate)
    print('optimized_frame_count:------------------>', optimized_frame_count)
    try:
        if not os.path.exists(root_path + 'journey_image/' + video_name):
            os.makedirs(root_path + 'journey_image/' + video_name)
    except OSError:
        print('Error: Creating directory of sub directory')

    count = 1
    success = True
    while success:
        frame_id = video_cap.get(1)  # current frame number
        success, image = video_cap.read()
        abs_fps = math.floor(frame_rate)
        if not success:
            break
        if frame_id % abs_fps == 0:
            filename = root_path + "journey_image/" + video_name + "/" + video_name + "_image_" + str(count) + ".jpg"
            cv2.imwrite(filename, image)
            count += 1

            if count <= optimized_frame_count:
                percentage = (count / optimized_frame_count) * 100
                # print('percentage------------>', str(percentage))
            else:
                break
    return video_name


# -------------------------------------------------------------------------------------------------------------------- #
# Method - 2: Read the journey xml file and write the fid, longitude, latitude details into another csv file

def extract_location():
    video = video_name
    with open(journey_location_csv + video + '.csv', 'w') as f:
        # f.write('fid,lat,long\n')

        tree = et.parse(xml_file_name + video + '.xml')
        root = tree.getroot()
        global fid, lat, long
        for c in root.iter('ExtendedData'):
            for a in c.iter('SchemaData'):
                for b in a.findall('SimpleData'):
                    # print(b.attrib)
                    if b.attrib['name'] == 'FID':
                        fid = b.text
                        # print(fid)
                    if b.attrib['name'] == 'Lat':
                        lat = b.text
                        # print(lat)
                    if b.attrib['name'] == 'Lon':
                        long = b.text
                        # print(long)

                        # print('{}-{}-{}'.format(fid, lat, long))
                        f.write('{},{},{}\n'.format(fid, lat, long))
                        # print('wrote')
                        # print("-------------------------------------------")


# -------------------------------------------------------------------------------------------------------------------- #
# Method - 3: Tag the geo location to the corresponding frame and predict the road signs in each frame.


def predict_road_signs():
    execute_in_order(os.path.join(root_path, 'journey_image', video_name), optimized_frame_count, video_name)


def pedestrian_crossing_inference():
    execute_in_order_pedestrian(os.path.join(root_path, 'journey_image', video_name), optimized_frame_count, video_name)


# -------------------------------------------------------------------------------------------------------------------- #

# Method - 4: Display the details of each identified image

def display_prediction_details(image_name, crosswalk_param):
    global lat, long, search_fid, sign_name, accuracy
    video = image_name.split('.')[0].split('_image')[0]
    frame_id = image_name.split('_')[-1].split(".")[0]
    with open(db_data_csv + video + '.csv') as f:
        reader = csv.reader(f)
        file_path = ''
        for row in reader:
            search_fid = str(row).strip('[]').split(',')[0].strip("' '")
            image_path = os.path.join(root_path, 'journey_image', video, image_name)
            print("Image path:-------------->", image_path)
            if search_fid == frame_id:
                lat = str(row).strip('[]').split(',')[1].strip("' '")
                long = str(row).strip('[]').split(',')[2].strip("' '")

                # Check if the inference is for a pedestrian crossing or signboard
                if crosswalk_param == "CROSSWALK":
                    values = display_single_image_details_crossing(image_path)
                else:
                    values = display_single_image_details(image_path)

                image = values[0]

                try:
                    if not os.path.exists('static/inference_image/' + video):
                        os.makedirs('static/inference_image/' + video)
                except OSError:
                    print('Error: Creating directory of sub directory')

                file_path = 'static/inference_image/' + video + '/' + video + '_' + frame_id + '.jpg'

                cv2.imwrite(file_path, image)
                sign_name = values[1]
                accuracy = values[2]
                # inference_time = str(values[3])
                # print('inference time from -> ' + inference_time)
                prop = [lat, long, sign_name, accuracy]
                break
        ret_val = dict(lat=lat, long=long, sign_name=sign_name, accuracy=accuracy, file_path=file_path)
    return ret_val


# -------------------------------------------------------------------------------------------------------------------- #

def remove_duplicates(video):
    global bes_t, idx_row, best_row_id, temp_data
    # video = 'journey_video_0001'
    # print(video_name)
    # video = video_name

    data = []
    temp_data = []
    final_result = []
    bes_t = ''
    with open(db_data_csv + video + '.csv') as f:
        reader = csv.reader(f)
        for record in reader:
            data.append(record)
    idx_row = 0
    best_row_id = 0
    final = ['default', 'default', 'default', 'default', '0']
    # final = []
    data.append(final)

    for row in data[idx_row:]:
        if idx_row + 1 < len(data):
            current_row = row
            current_name = current_row[3]

            next_row = data[idx_row + 1]
            next_name = next_row[3]

            if current_row not in temp_data and current_name is not None and int(current_row[4]) >= 65:
                temp_data.append(current_row)
                # print("Temp---------->", temp_data)

            if current_name == next_name and int(next_row[4]) >= 65:
                temp_data.append(next_row)
                idx_row = idx_row + 1
                # print('selected:', temp_data)

            elif current_name != next_name and len(temp_data) == 1 and current_name is not None and int(
                    current_row[4]) >= 70:
                if current_row not in final_result:
                    final_result.append(current_row)
                    # print("Final---------->", final_result)
                    idx_row = int(current_row[0])
            else:
                temp_idx_row = 0
                idx_t = 0
                for t in temp_data[temp_idx_row:]:
                    if idx_t + 1 < len(temp_data):
                        cur_t = temp_data[temp_idx_row]
                        nex_t = temp_data[idx_t + 1]
                        bes_t = cur_t
                        # if Decimal(cur_t[4].strip(' %')) > Decimal(nex_t[4].strip(' %')) and
                        # Decimal(cur_t[4].strip(' %')) >= 65.00:
                        if int(cur_t[4]) > int(nex_t[4]):
                            bes_t = cur_t
                            temp_idx_row = temp_idx_row
                        elif int(cur_t[4]) < int(nex_t[4]):
                            bes_t = nex_t
                            temp_idx_row = idx_t + 1
                        idx_t = idx_t + 1
                        idx_row = int(nex_t[0])
                        # print('next iteration id', idx_row)

                if bes_t not in final_result:
                    # print('best', bes_t)
                    if bes_t is not '':
                        final_result.append(bes_t)
                        # print('final final---------->', final_result)
                del temp_data[:]

    print("FINAL RES", final_result)
    return final_result


# --------------------------------------------------------------------------------------#


def display_inference_details(image_name, model_param):
    global sign_name, accuracy, inference_time
    image_path = os.path.join(root_path, 'test_images', image_name)
    # Check if the inference is for a pedestrian crossing or signboard
    print("model param->" + model_param)
    if model_param == "PC":
        values = display_single_image_details_crossing(image_path)
    else:
        values = display_single_image_details(image_path)

    image = values[0]

    try:
        if not os.path.exists('static/test_images/detected/' + image_name):
            os.makedirs('static/test_images/detected/' + image_name)
    except OSError:
        print('Error: Creating directory of sub directory')

    file_path = 'static/test_images/detected/' + image_name + '.jpg'

    cv2.imwrite(file_path, image)
    sign_name = values[1]
    accuracy = values[2]
    inference_time = str(values[3])
    ret_val = dict(sign_name=sign_name, accuracy=accuracy, inference_time=inference_time, file_path=file_path)
    return ret_val
