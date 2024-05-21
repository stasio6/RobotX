import cv2
import numpy as np
from file_utils import load_target_images_pickle, save_target_images_pickle
from calibrate_camera import undistort_image

TARGET_IMAGE_SIZES = (800, 800) # TODO: Tune
TARGET_IMAGES_LOAD_FROM_FILE = True # TODO: Fix False, currently not working
TARGET_IMAGES_PICKLE_PATH = "target_images.pkl"
CV_NUMBER_CORNERS_DETECTED = 1000
CV_CORNERS_QUALITY_LEVEL = 0.01
CV_CORNERS_MIN_DISTANCE = 30
CV_CORNERS_MATCHING_MAX_DISTANCE = 30

def load_target_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE) # TODO: Don't read it from file
    if TARGET_IMAGE_SIZES is not None:
        img = cv2.resize(img, TARGET_IMAGE_SIZES) # TODO: Maybe remove the resizing?
    return img

def load_camera_image(path, useColor=False):
    color = cv2.IMREAD_COLOR if useColor else cv2.IMREAD_GRAYSCALE
    camera_image = cv2.imread(path, color)
    # camera_image = undistort_image(camera_image)
    return camera_image

def prepare_target_images(target_images, calculate_key_descriptors):
    if TARGET_IMAGES_LOAD_FROM_FILE:
        for target_image in target_images:
            image = load_target_image(target_image["path"])
            target_image["descriptors"] = calculate_key_descriptors(image)
            target_image["image_shape"] = image.shape
        # save_target_images_pickle(TARGET_IMAGES_PICKLE_PATH, target_images) # TODO: Doesn't work
    else:
        target_images = load_target_images_pickle(TARGET_IMAGES_PICKLE_PATH)
    return target_images

def get_corners(img, camera_image_path=None):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(img, CV_NUMBER_CORNERS_DETECTED, CV_CORNERS_QUALITY_LEVEL, CV_CORNERS_MIN_DISTANCE)
    corners = corners_to_subpix2(img, corners)
    # draw_image_corners(img, corners)

    return corners

def corners_to_subpix2(img, corners):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), criteria)
    return corners

def get_closest_corners(img, targets, corners):
    res = []
    max_dist = CV_CORNERS_MATCHING_MAX_DISTANCE
    for t in targets:
        best = (max_dist, t)
        for c in corners:
            if np.linalg.norm(c - t) < best[0]:
                best = (np.linalg.norm(c - t), c[0])
        res.append(best[1])
    return res

