#!/usr/bin/python3

import time
from object_detection import detect_all_targets
from cam import SetInterval
from cam import single as take_picture

PIPELINE_STARTUP_DELAY_S = 10.0
PIPELINE_INTERVAL_DELAY_S = 3.0
PIPELINE_NUM_MAX_CAPTURES = 10
PIPELINE_IMAGE_ROOT_PATH = "captures/jetson_capture_"
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

def get_gps():
    print("GPS NOT IMPLEMENTED")

def run_object_detect(image_path):
    target_paths = [
        {
            "name": "target_n",
            "path": PIPELINE_TARGET_N_PATH,
        },
        {
            "name": "target_r",
            "path": PIPELINE_TARGET_R_PATH,
        },
        {
            "name": "target_heli",
            "path": PIPELINE_TARGET_HELI_PATH,
        }
    ]
    return detect_all_targets(image_path, target_paths)

def localize_objects(current_drone_gps, detected_objects):
    print("LOCALIZE NOT IMPLEMENTED")

def aggregate_results(object_locations):
    print("AGGREGATE NOT IMPLEMENTED")

def pipeline(iter_count):
    path = PIPELINE_IMAGE_ROOT_PATH + int(time.time()) + "_" + '{:05d}'.format(itercount) + '.jpg'
    gps = get_gps()
    take_picture(path, PIPELINE_IMAGE_COLOR)
    detected_objects = run_object_detect(path)
    object_locations = localize_objects(gps, detected_objects)
    aggregate_results(object_locations)

def exceute_pipeline():
    ctr = 1
    interval_handler = None

    def pipeline_handler():
        nonlocal ctr
        pipeline(ctr)
        if ctr > PIPELINE_NUM_MAX_CAPTURES:
            interval_handler.cancel()
        ctr += 1

    interval_handler = SetInterval(float(PIPELINE_INTERVAL_DELAY_S), pipeline_handler)
