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
from component.processor import IMG_SIZE

# Variable declaration
root_path = 'C:/Users/user/PycharmProjects/cdap_team_web/static/'
xml_file_name = 'C:/Users/user/PycharmProjects/cdap_team_web/static/video/xml/'
journey_location_csv = 'C:/Users/user/PycharmProjects/cdap_team_web/static/video/journey_csv/'
db_data_csv = 'C:/Users/user/PycharmProjects/cdap_team_web/component/db/'

getcontext().prec = 16
model = 'model.ckpt-70393.data-00000-of-00001'


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
    frame_rate = round(video_cap.get(cv2.CAP_PROP_FPS))
    print('frame_rate:------------------>', frame_rate)
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

                        print('{}-{}-{}'.format(fid, lat, long))
                        f.write('{},{},{}\n'.format(fid, lat, long))
                        # print('wrote')
                        print("-------------------------------------------")


# -------------------------------------------------------------------------------------------------------------------- #
# Method - 3: Tag the geo location to the corresponding frame and predict the road signs in each frame.


def predict_road_signs():
    execute_in_order(os.path.join(root_path, 'journey_image', video_name), optimized_frame_count, video_name)
    # global latitude, longitude, items
    # items = []
    # video = video_name
    # with open(db_data_csv + video + '.csv', 'w') as f:
        # f.write('fid,lat,long,sign,accuracy\n')
        # image_id = 1
        # for img in tqdm(os.listdir(os.path.join(root_path, 'journey_image', video))):

        # # print('Image id-------------->', image_id)
        # image_path = (os.path.join(root_path, 'journey_image', video, video + '_image_' + str(image_id) + '.jpg'))
        # # print('image_path------------>', image_path)
        # image = cv2.resize(cv2.imread(image_path, cv2.IMREAD_COLOR), (IMG_SIZE, IMG_SIZE))
        # data = image.reshape(IMG_SIZE, IMG_SIZE, 3)
        #
        # model_out = model.predict([data])[0]
        # value = np.argmax(model_out)
        # print('value number of the identified label------------>', value)
        # if value == 0:
        #     str_label = 'Children crossing ahead'
        # elif value == 1:
        #     str_label = 'Double bend to left ahead'
        # elif value == 2:
        #     str_label = 'Double bend to right ahead'
        # elif value == 3:
        #     str_label = 'Dual carriage way starts ahead'
        # elif value == 4:
        #     str_label = 'Hospital'
        # elif value == 5:
        #     str_label = 'Left bend ahead'
        # elif value == 6:
        #     str_label = 'Level crossing with gates ahead'
        # elif value == 7:
        #     str_label = 'Narrow bridge ahead'
        # elif value == 8:
        #     str_label = 'No entry'
        # elif value == 9:
        #     str_label = 'No honking'
        # elif value == 10:
        #     str_label = 'No left turn'
        # elif value == 11:
        #     str_label = 'No parking'
        # elif value == 12:
        #     str_label = 'No parking and standing'
        # elif value == 13:
        #     str_label = 'No parking on even days'
        # elif value == 14:
        #     str_label = 'No parking on odd days'
        # elif value == 15:
        #     str_label = 'No right turn'
        # elif value == 16:
        #     str_label = 'No u turn'
        # elif value == 17:
        #     str_label = 'Pass either side'
        # elif value == 18:
        #     str_label = 'Pass left side'
        # elif value == 19:
        #     str_label = 'Pass right side'
        # elif value == 20:
        #     str_label = 'Right bend ahead'
        # elif value == 21:
        #     str_label = 'Road closed for all vehicles'
        # elif value == 22:
        #     str_label = 'Round about ahead'
        # elif value == 23:
        #     str_label = 'Stop'
        # elif value == 24:
        #     str_label = 'Turn left ahead'
        # elif value == 25:
        #     str_label = 'Turn right ahead'
        # elif value == 26:
        #     str_label = 'U turn'
        #
        # accuracy = str(model_out[np.argmax(model_out)] * 100) + ' %'

        # with open(journey_location_csv + video + '.csv') as a:
        #     # print('opened')
        #     reader = csv.reader(a)
        #     for row in reader:
        #         # print(row)
        #         search_fid = str(row).strip('[]').split(',')[0].strip("' '")
        #         # print(search_fid)
        #         if search_fid == str(image_id):
        #             latitude = str(row).strip('[]').split(',')[1].strip("' '")
        #             longitude = str(row).strip('[]').split(',')[2].strip("' '")
        #             # print('<----------------------->')
        #             # print('Image Id---------------->', image_id)
        #             # print('latitude---------------->', latitude)
        #             # print('longitude--------------->', longitude)
        #             # print('Sign name--------------->', str_label)
        #             # print('accuracy---------------->', accuracy)
        #             items = [image_id, latitude, longitude, str_label, accuracy]
        #             f.write('{},{},{},{},{}\n'.format(items[0], items[1], items[2], items[3], items[4]))
        #             break
        # image_id = image_id + 1


# -------------------------------------------------------------------------------------------------------------------- #

# Method - 4: Display the details of each identified image

def display_prediction_details(image_name):
    global lat, long, search_fid, sign_name, accuracy
    video = image_name.split('.')[0].split('_image')[0]
    frame_id = image_name.split('_')[-1].split(".")[0]
    with open(db_data_csv + video + '.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            search_fid = str(row).strip('[]').split(',')[0].strip("' '")
            if search_fid == frame_id:
                lat = str(row).strip('[]').split(',')[1].strip("' '")
                long = str(row).strip('[]').split(',')[2].strip("' '")
                sign_name = str(row).strip('[]').split(',')[3].strip("' '")
                accuracy = str(row).strip('[]').split(',')[4].strip("' '")
                prop = [lat, long, sign_name, accuracy]
                break
        ret_val = dict(lat=lat, long=long, sign_name=sign_name, accuracy=accuracy)
    return ret_val


# -------------------------------------------------------------------------------------------------------------------- #

# Method - 5: Remove duplicated image information values that are been written csv

# def remove_duplicates(video):
#     global bes_t, idx_row, best_row_id, temp_data
#     # video = 'journey_video_0001'
#     # print(video_name)
#     # video = video_name
#
#     data = []
#     temp_data = []
#     final_result = []
#
#     with open(db_data_csv + video + '.csv') as f:
#         reader = csv.reader(f)
#         for record in reader:
#             data.append(record)
#     idx_row = 0
#     best_row_id = 0
#     final = ['default', 'default', 'default', 'default', 'default']
#     data.append(final)
#
#     for row in data[idx_row:]:
#         if idx_row + 1 < len(data):
#             current_row = row
#             current_name = current_row[3]
#
#             next_row = data[idx_row + 1]
#             next_name = next_row[3]
#
#             if current_row not in temp_data:
#                 temp_data.append(current_row)
#
#             if current_name is not None and current_name == next_name:
#                 temp_data.append(next_row)
#                 idx_row = idx_row + 1
#                 # print('selected:', temp_data)
#
#             elif current_name != next_name and len(temp_data) == 1 and current_name is not None and int(cur_t[4]) >= 65:
#                 if current_row not in final_result:
#                     final_result.append(current_row)
#                     idx_row = int(current_row[0])
#             else:
#                 temp_idx_row = 0
#                 idx_t = 0
#                 for t in temp_data[temp_idx_row:]:
#                     if idx_t + 1 < len(temp_data):
#                         cur_t = temp_data[temp_idx_row]
#                         nex_t = temp_data[idx_t + 1]
#                         bes_t = cur_t
#
#                         # if Decimal(cur_t[4].strip(' %')) > Decimal(nex_t[4].strip(' %')) and Decimal(cur_t[4].strip(' %')) >= 65.00:
#                         if int(cur_t[4]) > int(nex_t[4]) and int(cur_t[4]) >= 65:
#
#                             bes_t = cur_t
#                             temp_idx_row = temp_idx_row
#
#                         elif int(cur_t[4]) < int(nex_t[4]) and int(nex_t[4]) >= 65:
#                             bes_t = nex_t
#                             temp_idx_row = idx_t + 1
#
#                         idx_t = idx_t + 1
#                         idx_row = int(nex_t[0])
#                         print('next iteration id', idx_row)
#                 print('best', bes_t)
#                 if bes_t not in final_result:
#                     final_result.append(bes_t)
#
#                 del temp_data[:]
#
#     print("FINAL RES", final_result)


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
            print("Data---------->", data)
    idx_row = 0
    best_row_id = 0
    final = ['default', 'default', 'default', 'default', '0']
    data.append(final)

    for row in data[idx_row:]:
        if idx_row + 1 < len(data):
            current_row = row
            current_name = current_row[3]

            next_row = data[idx_row + 1]
            next_name = next_row[3]

            if current_row not in temp_data and current_name is not None and int(current_row[4]) >= 65:
                temp_data.append(current_row)
                print("Temp---------->", temp_data)

            if current_name == next_name and int(next_row[4]) >= 65:
                temp_data.append(next_row)
                idx_row = idx_row + 1
                # print('selected:', temp_data)

            elif current_name != next_name and len(temp_data) == 1 and current_name is not None and int(current_row[4]) >= 85:
                if current_row not in final_result:
                    final_result.append(current_row)
                    print("Final---------->", final_result)
                    idx_row = int(current_row[0])
            else:
                temp_idx_row = 0
                idx_t = 0
                for t in temp_data[temp_idx_row:]:
                    if idx_t + 1 < len(temp_data):
                        cur_t = temp_data[temp_idx_row]
                        nex_t = temp_data[idx_t + 1]
                        bes_t = cur_t

                        # if Decimal(cur_t[4].strip(' %')) > Decimal(nex_t[4].strip(' %')) and Decimal(cur_t[4].strip(' %')) >= 65.00:
                        if int(cur_t[4]) > int(nex_t[4]):
                            bes_t = cur_t
                            temp_idx_row = temp_idx_row
                        elif int(cur_t[4]) < int(nex_t[4]):
                            bes_t = nex_t
                            temp_idx_row = idx_t + 1
                        idx_t = idx_t + 1
                        idx_row = int(nex_t[0])
                        print('next iteration id', idx_row)

                if bes_t not in final_result:
                    print('best', bes_t)
                    final_result.append(bes_t)
                    print('final final---------->', final_result)

                del temp_data[:]

    print("FINAL RES", final_result)

# remove_duplicates('journey_video_0003')
