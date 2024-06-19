import cv2
import numpy as np
import sys
from cv_utilities import get_closest_corners, detect_optimal_corners, detect_polygon_corners, normalize_corners
from cv_debugging import draw_image_corners
from time_utils import time_elapsed

CV_GOOD_MATCHES_NEEDED = 20
CV_CORNER_MATCH_UNIQUENESS = 0.80
CV_USE_DENOISING = False # Turns out denoising makes results worse
CV_USE_OPTIMAL_CORNERS = True
CV_USE_POLYGON_CORNERS = True

sift = cv2.SIFT_create()

def denoise_image(img):
    return cv2.fastNlMeansDenoising(img)

def detect_all_targets(image_data, target_objs):
    # time_elapsed("Start", False)
    # print("Start")
    
    camera_image = image_data["image"]
    # time_elapsed("Image loaded")
    if CV_USE_DENOISING:
        camera_image = denoise_image(camera_image)
    # time_elapsed("Image denoised")
    assert CV_USE_OPTIMAL_CORNERS or CV_USE_POLYGON_CORNERS
    if CV_USE_POLYGON_CORNERS and CV_USE_OPTIMAL_CORNERS:
        detected_corners = get_closest_corners(detect_polygon_corners(camera_image), detect_optimal_corners(camera_image), 5)
    elif CV_USE_OPTIMAL_CORNERS:
        detected_corners = detect_optimal_corners(camera_image)
    else:
        detected_corners = detect_polygon_corners(camera_image)
    camera_image_kd = calculate_key_descriptors(camera_image)
    # time_elapsed("Preprocessing")
    # draw_image_corners(camera_image, detect_polygon_corners(camera_image), detect_optimal_corners(camera_image), detected_corners)

    res_all = []
    for target_obj in target_objs:
        try:
            found, corners = detect_object_sift(target_obj["descriptors"], camera_image_kd, target_obj["image_shape"])
            precise_corners = get_closest_corners(corners, detected_corners, 50)
        except:
            found = False
            precise_corners = []
            print("Exception occured")
        # time_elapsed("SIFT")
        result = {
            "name": target_obj["name"],
            "corners": precise_corners,
            "found": found
        }
        res_all.append(result)
    return res_all

def calculate_key_descriptors(image):
    return sift.detectAndCompute(image, None)

def detect_object_sift(target_image_kd, camera_image_kd, target_image_shape):

    # Detect keypoints and compute descriptors for both images
    target_keypoints, target_descriptors = target_image_kd
    camera_keypoints, camera_descriptors = camera_image_kd

    # Create FLANN-based matcher
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)
    matcher = cv2.FlannBasedMatcher(index_params, search_params)

    # Match descriptors using KNN
    matches = matcher.knnMatch(target_descriptors, camera_descriptors, k=2)

    # Apply ratio test to filter good matches
    good_matches = []
    for m, n in matches:
        if m.distance < CV_CORNER_MATCH_UNIQUENESS * n.distance:
            good_matches.append(m)

    # print(len(good_matches))
    # Check if a reasonable match found
    if len(good_matches) < CV_GOOD_MATCHES_NEEDED:
        return False, []

    # Extract location of good matches
    target_points = np.float32([target_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    camera_points = np.float32([camera_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # Estimate homography using RANSAC
    homography, _ = cv2.findHomography(target_points, camera_points, cv2.RANSAC)

    # Get the corners of the target image
    target_corners = np.float32([[0, 0], [target_image_shape[1], 0], [target_image_shape[1], target_image_shape[0]], [0, target_image_shape[0]]]).reshape(-1, 1, 2)
    
    # Transform the corners using the homography
    camera_corners = cv2.perspectiveTransform(target_corners, homography)

    corners = normalize_corners(camera_corners)
    corners.reverse()

    return True, corners
