#!/usr/bin/python3

import cv2
from object_detection import detect_all_targets, calculate_key_descriptors
from cv_utilities import load_target_image, prepare_target_images
from cv_debugging import draw_image_objects
from localization import localize_objects
from aggregator import aggregate_results
from file_utils import save_capture_data, save_json_data, read_test_data
from time_utils import get_current_datetime
from pymavlink import mavutil
from cam import SetInterval
from cam import capture_image as take_picture 
from pixhawk_utils import get_pixhawk_data

PIXHAWK_URL = "/dev/ttyTHS1"

PIPELINE_STARTUP_DELAY_S = 10.0
PIPELINE_INTERVAL_DELAY_S = 3.0
PIPELINE_NUM_MAX_CAPTURES = 10
# all data saved under PIPELINE_DATA_SAVE_ROOT/PIPELINE_DATA_SAVE_SUB_PREFIX + $TIME_STAMP/*
PIPELINE_DATA_SAVE_ROOT = 'data/'
PIPELINE_DATA_SAVE_SUB_PREFIX = ''
PIPELINE_IMAGE_ROOT = 'captures/'
PIPELINE_JSON_ROOT = 'json/'
PIPELINE_SAVE_PREFIX = 'jetson_capture_'
PIPELINE_RESULT_ROOT = 'results/'
PIPELINE_RESULT_PATH_PREFIX = PIPELINE_RESULT_ROOT + PIPELINE_SAVE_PREFIX
PIPELINE_IMAGE_PATH_PREFIX = PIPELINE_IMAGE_ROOT + PIPELINE_SAVE_PREFIX
PIPELINE_JSON_PATH_PREFIX = PIPELINE_JSON_ROOT + PIPELINE_SAVE_PREFIX
PIPELINE_TARGET_N_PATH = "targets/target_n.jpg"
PIPELINE_TARGET_R_PATH = "targets/target_r.jpg"
PIPELINE_TARGET_HELI_PATH = "targets/helipad.jpg"
PIPELINE_IMAGE_COLOR = False
PIPELINE_PICTURE_ONLY = False
PIPELINE_SAVE_ROOT = ""
# Testing variables
PIPELINE_TEST_MODE = False
PIPELINE_TEST_DIRECTORY = "test/drone/240518_153501"

"""
Pipeline: (repeated every n seconds)
    Capture Image + GPS -> (Image File path, GPS Returned)
    Detect Object with image file -> (Objects with detect and coords)
    Localisation Object -> (Returns Object + location)
    Aggregate Results -> (Returns Object + location)
"""

def get_cam_metadata():
    master = mavutil.mavlink_connection(PIXHAWK_URL, baud=57600)
    metadata = get_pixhawk_data(master)
    return metadata

def pipeline(iter_count, target_objs):
    print("Capturing Picture:", iter_count)
    image_path = PIPELINE_SAVE_ROOT + "/" + PIPELINE_IMAGE_PATH_PREFIX + '{:05d}'.format(iter_count) + '.jpg'
    json_path = PIPELINE_SAVE_ROOT + "/" +  PIPELINE_JSON_PATH_PREFIX + '{:05d}'.format(iter_count) + '.json'
    result_path = PIPELINE_SAVE_ROOT + "/" + PIPELINE_RESULT_PATH_PREFIX + '{:05d}'.format(iter_count) + '.json'
    try:
        if not PIPELINE_TEST_MODE:
            print("Getting Metadata")
            metadata = get_cam_metadata()
            print("Taking Picture")
            image = take_picture()
            print("Saving JSON data")
            image_data = save_json_data(json_path, image_path, image, metadata)
        else:
            metadata, image_data = read_test_data(iter_count, PIPELINE_TEST_DIRECTORY)

        if not PIPELINE_PICTURE_ONLY:
            print("Live Detect Mode, detecting objects")
            detected_objects = detect_all_targets(image_data, target_objs)
            if PIPELINE_TEST_MODE:
                draw_image_objects(image_data["image_path"], detected_objects)
            print("Running Localisation")
            object_locations = localize_objects(metadata, detected_objects)
            print("Aggregating Results")
            aggregate_data = aggregate_results(object_locations)
            print("Saving capture data")
            if PIPELINE_TEST_MODE:
                print("Results:\n", object_locations, "\n", aggregate_data)
            else:
                save_capture_data(result_path, object_locations, aggregate_data)
    except Exception as error:
        print("Error in pipeline:", error)

def exceute_pipeline():
    print("Preparing Pipeline")
    ctr = 1
    interval_handler = None

    target_objs = [
        { "name": "target_n", "path": PIPELINE_TARGET_N_PATH },
        { "name": "target_r", "path": PIPELINE_TARGET_R_PATH }
#        { "name": "helipad", "path": PIPELINE_TARGET_HELI_PATH }
    ]
    print("Preparing Target Images")
    target_objs = prepare_target_images(target_objs, calculate_key_descriptors)
    
    print("Starting pipeline")
    def pipeline_handler():
        nonlocal ctr
        pipeline(ctr, target_objs)
        if ctr >= PIPELINE_NUM_MAX_CAPTURES:
            interval_handler.cancel()
        ctr += 1

    interval_handler = SetInterval(float(PIPELINE_INTERVAL_DELAY_S), pipeline_handler)

def prepare_save_directory():
    import os
    directory = ''
    directory += PIPELINE_DATA_SAVE_ROOT
    directory += PIPELINE_DATA_SAVE_SUB_PREFIX
    directory += get_current_datetime()
    try:
        os.mkdir(directory)
        print(f"Directory '{directory}' created successfully.")
    except Exception as err:
        print("Exception occurred while trying to create directory:", err)
        exit(1)
    global PIPELINE_SAVE_ROOT
    PIPELINE_SAVE_ROOT = directory
    try:
        os.mkdir(directory + "/" + PIPELINE_IMAGE_ROOT)
        os.mkdir(directory + "/" + PIPELINE_JSON_ROOT)
        os.mkdir(directory + "/" + PIPELINE_RESULT_ROOT)
    except Exception as err:
        print("Exception occurred while trying to create directory:", err)
        exit(1)

def clean():
    import os
    import glob
    files = glob.glob(PIPELINE_IMAGE_ROOT + "*.jpg")
    for f in files:
        os.remove(f)
    files = glob.glob(PIPELINE_JSON_ROOT + "*.json")
    for f in files:
        os.remove(f)

if __name__ == "__main__":
    import argparse
    print("Setting up Parser")
    parser = argparse.ArgumentParser(description='Capture Pipeline')
    parser.add_argument('--interval', type=float, default=PIPELINE_INTERVAL_DELAY_S, help='Interval between captures')
    parser.add_argument('--num-captures', type=int, default=PIPELINE_NUM_MAX_CAPTURES, help='Number of captures')
    parser.add_argument('--image-root', type=str, default=PIPELINE_IMAGE_PATH_PREFIX, help='Image root path')
    parser.add_argument('--json-root', type=str, default=PIPELINE_JSON_PATH_PREFIX, help='JSON root path')
    parser.add_argument('--save-prefix', type=str, default=PIPELINE_SAVE_PREFIX, help='Files will be saved as prefix_ + timestamp.jpg/json')
    parser.add_argument('--target-n', type=str, default=PIPELINE_TARGET_N_PATH, help='Target N path')
    parser.add_argument('--target-r', type=str, default=PIPELINE_TARGET_R_PATH, help='Target R path')
    parser.add_argument('--target-heli', type=str, default=PIPELINE_TARGET_HELI_PATH, help='Target Helipad path')
    parser.add_argument('--color', type=bool, default=PIPELINE_IMAGE_COLOR, help='Color image')
    parser.add_argument('--clean', action='store_true', default=False, help='Clean up images and jsons')
    parser.add_argument('--picture-only', action='store_true', default=False, help='Only take pictures')
    parser.add_argument('--test-mode', action='store_true', default=False, help='This mode makes pipeline read images from file, not take photos')
    args = parser.parse_args()
    if args.clean:
        clean()
    PIPELINE_INTERVAL_DELAY_S = args.interval
    PIPELINE_NUM_MAX_CAPTURES = args.num_captures
    PIPELINE_IMAGE_PATH_PREFIX = args.image_root
    PIPELINE_JSON_PATH_PREFIX = args.json_root
    PIPELINE_TARGET_N_PATH = args.target_n
    PIPELINE_TARGET_R_PATH = args.target_r
    PIPELINE_TARGET_HELI_PATH = args.target_heli
    PIPELINE_IMAGE_COLOR = args.color
    PIPELINE_PICTURE_ONLY = args.picture_only
    PIPELINE_TEST_MODE = args.test_mode

    if not PIPELINE_TEST_MODE:
        prepare_save_directory()
    exceute_pipeline()
