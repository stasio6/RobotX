import cv2
import numpy as np
import sys
from cv_utilities import get_closest_corners, get_corners, draw_image_corners
from utils import time_elapsed

sift = cv2.SIFT_create()

def load_target_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE) # TODO: Don't read it from file
    img = cv2.resize(img, (800, 800)) # TODO: Maybe remove the resizing?
    return img

def prepare_target_images(target_images):
    for target_image in target_images:
        target_image["image"] = load_target_image(target_image["path"])
        target_image["descriptors"] = calculate_key_descriptors(target_image["image"])
    return target_images

def denoise_image(img):
    return cv2.fastNlMeansDenoising(img)

def detect_all_targets(camera_image_path, target_images):
    time_elapsed("Start", False)
    print("Start")
    camera_image = cv2.imread(camera_image_path, cv2.IMREAD_GRAYSCALE)
    time_elapsed("Image loaded")
    camera_image = denoise_image(camera_image)
    time_elapsed("Image denoised")
    subpixel_corners = get_corners(camera_image)
    camera_image_kd = calculate_key_descriptors(camera_image)
    time_elapsed("Preprocessing")
    # draw_image_corners(draw_img, subpixel_corners)

    res_all = []
    for target_obj in target_images:
        found, corners = detect_object_sift(target_obj["descriptors"], camera_image_kd, target_obj["image"].shape)
        precise_corners = get_closest_corners(camera_image, corners, subpixel_corners)
        time_elapsed("SIFT")
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
        if m.distance < 0.80 * n.distance:
            good_matches.append(m)

    # print(len(good_matches))
    # Check if a reasonable match found
    if len(good_matches) < 20:
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

    corners = []
    for c in camera_corners:
        corners.append(c[0])
    return True, corners

    # Draw the matched region on the camera image
    # result_image = cv2.cvtColor(camera_image, cv2.COLOR_GRAY2BGR)
    # camera_corners = camera_corners.reshape(-1, 2)
    # pts = np.int32(camera_corners).reshape((-1, 1, 2))
    # cv2.polylines(result_image, [pts], True, (0, 255, 0), 2, cv2.LINE_AA)

    # # Display the result
    # cv2.imshow("Result", result_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
