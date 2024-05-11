#!/usr/bin/python3

import time
from object_detection import detect_all_targets, load_target_image
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

def run_object_detect(image_path, target_images):
    return detect_all_targets(image_path, target_images)

def localize_objects(current_drone_gps, detected_objects):
    print("LOCALIZE NOT IMPLEMENTED")

def aggregate_results(object_locations):
    print("AGGREGATE NOT IMPLEMENTED")

def pipeline(iter_count, target_images):
    path = PIPELINE_IMAGE_ROOT_PATH + str(time.time()) + "_" + '{:05d}'.format(iter_count) + '.jpg'
    gps = get_gps()
    take_picture(path, PIPELINE_IMAGE_COLOR)
    detected_objects = run_object_detect(path, target_images)
    object_locations = localize_objects(gps, detected_objects)
    aggregate_results(object_locations)

def exceute_pipeline():
    ctr = 1
    interval_handler = None

    target_images = [
        {
            "name": "target_n",
            "image": load_target_image(PIPELINE_TARGET_N_PATH),
        },
        {
            "name": "target_r",
            "image": load_target_image(PIPELINE_TARGET_R_PATH),
        },
        {
            "name": "target_heli",
            "image": load_target_image(PIPELINE_TARGET_HELI_PATH),
        }
    ]

    def pipeline_handler():
        nonlocal ctr
        pipeline(ctr, target_images)
        if ctr > PIPELINE_NUM_MAX_CAPTURES:
            interval_handler.cancel()
        ctr += 1

    interval_handler = SetInterval(float(PIPELINE_INTERVAL_DELAY_S), pipeline_handler)

if __name__ == "__main__":
    exceute_pipeline()
