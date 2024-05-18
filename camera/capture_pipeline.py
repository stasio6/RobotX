#!/usr/bin/python3

import time
import json
from object_detection import detect_all_targets, calculate_key_descriptors
from cv_utilities import load_target_image, prepare_target_images, draw_image_objects
from transformations import localize_objects
from aggregator import aggregate_results
# from pymavlink import mavutil
from cam import SetInterval
from cam import capture_image as take_picture 
from pixhawk_utils import get_pixhawk_data

PIXHAWK_URL = "<PIXHAWK_URL>"

PIPELINE_STARTUP_DELAY_S = 10.0
PIPELINE_INTERVAL_DELAY_S = 3.0
PIPELINE_NUM_MAX_CAPTURES = 10
PIPELINE_IMAGE_ROOT_PATH = "captures/jetson_capture_"
PIPELINE_JSON_ROOT_PATH = "json/jetson_capture_"
PIPELINE_TARGET_N_PATH = "targets/target_n.jpg"
PIPELINE_TARGET_R_PATH = "targets/target_r.jpg"
PIPELINE_TARGET_HELI_PATH = "targets/helipad.jpg"
PIPELINE_IMAGE_COLOR = False

"""
Pipeline: (repeated every n seconds)
    Capture Image + GPS -> (Image File path, GPS Returned)
    Detect Object with image file -> (Objects with detect and coords)
    Localisation Object -> (Returns Object + location)
    Aggregate Results

"""

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
    cv2.imwrite(image_path, image)
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file)
    json_data["image"] = image
    return json_data

def pipeline(iter_count, target_objs):
    image_path = PIPELINE_IMAGE_ROOT_PATH + str(time.time()) + "_" + '{:05d}'.format(iter_count) + '.jpg'
    json_path = PIPELINE_JSON_ROOT_PATH + str(time.time()) + "_" + '{:05d}'.format(iter_count) + '.json'
    try:
        metadata = get_cam_metadata()
        image = take_picture()
        image_data = save_json_data(json_path, image_path, image, metadata)
        
        detected_objects = detect_all_targets(image_data, target_objs)
        draw_image_objects("test/full/img2.jpg", detected_objects)
        object_locations = localize_objects(metadata, detected_objects)

        results = aggregate_results(object_locations)
    except Exception as error:
        print("An exception occurred:", error)

def exceute_pipeline():
    ctr = 1
    interval_handler = None

    target_objs = [
        { "name": "target_n", "path": PIPELINE_TARGET_N_PATH },
        { "name": "target_r", "path": PIPELINE_TARGET_R_PATH },
        { "name": "helipad", "path": PIPELINE_TARGET_HELI_PATH }
    ]
    target_objs = prepare_target_images(target_objs, calculate_key_descriptors)

    def pipeline_handler():
        nonlocal ctr
        pipeline(ctr, target_objs)
        if ctr > PIPELINE_NUM_MAX_CAPTURES:
            interval_handler.cancel()
        ctr += 1

    interval_handler = SetInterval(float(PIPELINE_INTERVAL_DELAY_S), pipeline_handler)

if __name__ == "__main__":
    exceute_pipeline()
