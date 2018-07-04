import os
from random import shuffle

import cv2
import numpy as np
from tqdm import tqdm

TRAIN_DIR = 'C:/Users/user/PycharmProjects/cdap_team_web/data_set/training_data_dir';
TEST_DIR = 'C:/Users/user/PycharmProjects/cdap_team_web/data_set/testing_data_dir';
IMG_SIZE = 32;


# Method 1 : Label the image


def label_image(img):

    # img = turn_left_ahead_00017.jpg
    word_label = img.split('.')[0]

    # 1
    if word_label.__contains__('children_crossing_ahead'):
        return [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 2
    elif word_label.__contains__('double_bend_to_left_ahead'):
        return [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 3
    elif word_label.__contains__('double_bend_to_right_ahead'):
        return [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # 4
    elif word_label.__contains__('dual_carriage_way_starts_ahead'):
        return [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 5
    elif word_label.__contains__('hospital'):
        return [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 6
    elif word_label.__contains__('left_bend_ahead'):
        return [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 7
    elif word_label.__contains__('level_crossing_with_gates_ahead'):
        return [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 8
    elif word_label.__contains__('narrow_bridge_ahead'):
        return [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 9
    elif word_label.__contains__('no_entry'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 10
    elif word_label.__contains__('no_horning'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 11
    elif word_label.__contains__('no_left_turn'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 12
    elif word_label.__contains__('no_parking'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 13
    elif word_label.__contains__('no_parking_and_standing'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 14
    elif word_label.__contains__('no_parking_on_even_days'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 15
    elif word_label.__contains__('no_parking_on_odd_days'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 16
    elif word_label.__contains__('no_right_turn'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 17
    elif word_label.__contains__('no_u_turn'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 18
    elif word_label.__contains__('pass_either_side'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # 19
    elif word_label.__contains__('pass_left_side'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]

    # 20
    elif word_label.__contains__('pass_right_side'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]

    # 21
    elif word_label.__contains__('right_bend_ahead'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]

    # 22
    elif word_label.__contains__('road_closed_for_all_vehicles'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]

    # 23
    elif word_label.__contains__('round_about_ahead'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]

    # 24
    elif word_label.__contains__('stop'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]

    # 25
    elif word_label.__contains__('turn_left_ahead'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]

    # 26
    elif word_label.__contains__('turn_right_ahead'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]

    # 27
    elif word_label.__contains__('u_turn'):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

# Method 2 : create the train data set


def create_training_data_set():

    training_data_set = []

    directories = [d for d in os.listdir(TRAIN_DIR)
                   if os.path.isdir(os.path.join(TRAIN_DIR, d))]

    for d in directories:
        for img in tqdm(os.listdir(os.path.join(TRAIN_DIR, d))):
            label = label_image(img)
            path = os.path.join(TRAIN_DIR, d, img)
            print("pathpathpath", path)
            img = cv2.resize(cv2.imread(path, cv2.IMREAD_COLOR), (IMG_SIZE, IMG_SIZE))
            training_data_set.append([np.array(img), np.array(label)])

    shuffle(training_data_set)
    np.save('C:/Users/user/PycharmProjects/cdap_team_web/data_set/npy/train_set.npy', training_data_set)
    print('Completed generating training data set!')
    return training_data_set


# Method 3 : Process the test data set

def process_test_data():

    testing_data_set = []

    for img in tqdm(os.listdir(TEST_DIR)):
        path = os.path.join(TEST_DIR, img)
        img_num = img.split('.')[0]
        print(str(img_num))
        img = cv2.resize(cv2.imread(path, cv2.IMREAD_COLOR), (IMG_SIZE, IMG_SIZE))
        testing_data_set.append([np.array(img), img_num])

    shuffle(testing_data_set)
    np.save('C:/Users/user/PycharmProjects/cdap_team_web/data_set/npy/test_data.npy',  testing_data_set)
    return testing_data_set


# Method calling

# train_data = create_training_data_set()
# if trained
train_data = np.load('C:/Users/user/PycharmProjects/video_data/train_set.npy')
# test_data = process_test_data()
