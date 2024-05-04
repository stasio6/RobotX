import cv2
import numpy as np
from calibrate_camera import load_coefficients

def get_corners(img):
    # print(img)
    corners = cv2.cornerHarris(img,2,3,0.04)
    # return corners
    # print("Corners:")
    # print(corners)
    dst = cv2.dilate(corners,None)
    th = 0.001
    ret, dst = cv2.threshold(dst,th*dst.max(),255,0)
    dst = np.uint8(dst)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst) # TODO: Maybe??? Check if better accuracy
    corners = centroids
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    # print("Centroids")
    # print(centroids)
    corners = cv2.cornerSubPix(img, np.float32(centroids), (5, 5), (-1, -1), criteria)
    for c in corners:
        img = cv2.circle(img, (c[0],c[1]), radius=10, color=(0, 255, 0), thickness=-10)
    # cv2.imshow("Shapes", cv2.resize(img, (800, 600)))
    # cv2.waitKey(0)
    return corners

# Inspired by https://docs.opencv.org/4.x/dc/d0d/tutorial_py_features_harris.html
def get_closest_corners(img, targets, corners):
    res = []
    max_dist = 10
    for t in targets:
        best = (max_dist, t)
        for c in corners:
            if np.linalg.norm(c - t) < best[0]:
                best = (np.linalg.norm(c - t), c)
        res.append(best[1])
    return res

def get_camera_pose(img, corners, object_side):
    camera_matrix, dist_matrix = load_coefficients()
    hl = object_side/2
    rvec, tvec = cv2.solvePnP([[-hl, hl], [hl, hl], [hl, -hl], [-hl, -hl]], corners, camera_matrix, cv::noArray())
    R = cv.Rodrigues(rvec)
    return R, t


def get_img_center(img, corners, camera_pose, object_side=150):
    relative_pose = get_camera_pose(img, corners, object_side)
    


