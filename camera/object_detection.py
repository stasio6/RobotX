import cv2
import numpy as np
import sys
from cv_utilities import get_closest_corners, get_corners, draw_image_corners
from utils import time_elapsed

TARGET_N_PATH = "targets/target_n.jpg"
TARGET_R_PATH = "targets/target_r.jpg"
TARGET_HELIPAD_PATH = "targets/helipad.jpg"

TARGET_N = None
TARGET_R = None
TARGET_HELIPAD = None

def load_target_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE) # TODO: Don't read it from file
    img = cv2.resize(img, (800, 800)) # TODO: Maybe remove the resizing?
    return img

def init():
    global TARGET_N, TARGET_R, TARGET_HELIPAD
    if not TARGET_N:
        TARGET_N = load_target_image(TARGET_N_PATH)
    if not TARGET_R:
        TARGET_R = load_target_image(TARGET_R_PATH)
    if not TARGET_HELIPAD:
        TARGET_HELIPAD = load_target_image(TARGET_HELIPAD_PATH)

def denoise_image(img):
    return cv2.fastNlMeansDenoising(img)

def detect_all(camera_image_path):
    init()
    camera_image = cv2.imread(camera_image_path, cv2.IMREAD_GRAYSCALE)
    camera_image = denoise_image(camera_image)
    subpixel_corners = get_corners(camera_image)
    # draw_image_corners(draw_img, subpixel_corners)

    res_all = []
    for target_img, name in [(TARGET_N, "target_N"), (TARGET_R, "target_R"), (TARGET_HELIPAD, "HELIPAD")]:
        time_elapsed("Start", False)
        found, corners = detect_object(camera_image, target_img)
        # time_elapsed("Object detection")
        precise_corners = get_closest_corners(camera_image, corners, subpixel_corners)
        time_elapsed("Done")
        result = {
            "name": name,
            "corners": precise_corners,
            "found": found
        }
        res_all.append(result)
    return res_all

def detect_object(camera_image, target_image):

    if target_image is None or camera_image is None:
        print("Failed to load images!")
        return False, []
    
    found, corners = detect_object_sift(target_image, camera_image)

    res = []
    for c in corners:
        res.append(c[0])
    return found, res

def detect_object_sift(target_image, camera_image):
    sift = cv2.SIFT_create()

    # Detect keypoints and compute descriptors for both images
    target_keypoints, target_descriptors = sift.detectAndCompute(target_image, None)
    camera_keypoints, camera_descriptors = sift.detectAndCompute(camera_image, None)

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
    target_corners = np.float32([[0, 0], [target_image.shape[1], 0], [target_image.shape[1], target_image.shape[0]], [0, target_image.shape[0]]]).reshape(-1, 1, 2)
    
    # Transform the corners using the homography
    camera_corners = cv2.perspectiveTransform(target_corners, homography)
    return True, camera_corners

    # Draw the matched region on the camera image
    # result_image = cv2.cvtColor(camera_image, cv2.COLOR_GRAY2BGR)
    # camera_corners = camera_corners.reshape(-1, 2)
    # pts = np.int32(camera_corners).reshape((-1, 1, 2))
    # cv2.polylines(result_image, [pts], True, (0, 255, 0), 2, cv2.LINE_AA)

    # # Display the result
    # cv2.imshow("Result", result_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
