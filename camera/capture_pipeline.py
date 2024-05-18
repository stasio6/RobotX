#!/usr/bin/python3

import time
import json
import cv2
from object_detection import detect_all_targets, calculate_key_descriptors
from cv_utilities import load_target_image, prepare_target_images, draw_image_objects
from transformations import localize_objects
from aggregator import aggregate_results
from pymavlink import mavutil
from cam import SetInterval
from cam import capture_image as take_picture 
from pixhawk_utils import get_pixhawk_data

PIXHAWK_URL = "/dev/ttyTHS1"

PIPELINE_STARTUP_DELAY_S = 10.0
PIPELINE_INTERVAL_DELAY_S = 3.0
PIPELINE_NUM_MAX_CAPTURES = 10
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

"""
Pipeline: (repeated every n seconds)
    Capture Image + GPS -> (Image File path, GPS Returned)
    Detect Object with image file -> (Objects with detect and coords)
    Localisation Object -> (Returns Object + location)
    Aggregate Results -> (Returns Object + location)
"""

def save_capture_data(path, localization_data, aggregation_data):
    json_data = {
        "localization": localization_data,
        "aggregation": aggregation_data
    }
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file)

def get_cam_metadata():
    master = mavutil.mavlink_connection(PIXHAWK_URL, baud=57600)
    metadata = get_pixhawk_data(master)
    return metadata

def save_json_data(json_path, image_path, image, metadata):
    json_data = {
            "path": image_path, 
            "gps": metadata["gps_data"],
            "imu": metadata["imu_data"],
            "att": metadata["att_data"],
        }
    print("Saving image to path:", image_path)
    cv2.imwrite(image_path, image)
    print("Saving JSON to path:", json_path)
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file)
    json_data["image"] = image
    return json_data

def pipeline(iter_count, target_objs):
    print("Pipeline Iteration:", iter_count)
    image_path = PIPELINE_IMAGE_PATH_PREFIX + str(int(time.time())) + "_" + '{:05d}'.format(iter_count) + '.jpg'
    json_path = PIPELINE_JSON_PATH_PREFIX + str(int(time.time())) + "_" + '{:05d}'.format(iter_count) + '.json'
    result_path = PIPELINE_RESULT_PATH_PREFIX + str(int(time.time())) + "_" + '{:05d}'.format(iter_count) + '.json'
    try:
        metadata = get_cam_metadata()
        image = take_picture()
        image_data = save_json_data(json_path, image_path, image, metadata)
        if not PIPELINE_PICTURE_ONLY:
            detected_objects = detect_all_targets(image_data, target_objs)
            object_locations = localize_objects(metadata, detected_objects)
            print(object_locations)
            aggregate_data = aggregate_results(object_locations)
            save_capture_data(result_path, object_locations, aggregate_data)
    except Exception as error:
        print("Error in pipeline:", error)

def exceute_pipeline():
    print("Preparing Pipeline")
    ctr = 1
    interval_handler = None

    target_objs = [
        { "name": "target_n", "path": PIPELINE_TARGET_N_PATH },
        { "name": "target_r", "path": PIPELINE_TARGET_R_PATH },
        { "name": "helipad", "path": PIPELINE_TARGET_HELI_PATH }
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

    exceute_pipeline()
