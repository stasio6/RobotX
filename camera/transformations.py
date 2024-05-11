import cv2
import numpy as np
from calibrate_camera import load_coefficients

def get_camera_pose(corners, square):
    camera_matrix, dist_matrix = load_coefficients()
    success, rvec, tvec = cv2.solvePnP(np.array(square), np.array(corners), camera_matrix, None, flags=cv2.SOLVEPNP_IPPE_SQUARE)
    if not success:
        print("SMUTACZ!")
    R = cv2.Rodrigues(rvec)[0]
    # print(rvec)
    # print(R)
    return R, tvec.reshape(-1)


def get_img_center(corners, camera_pose, object_side=150):
    hl = object_side/2
    square = [[-hl, hl, 0], [hl, hl, 0], [hl, -hl, 0], [-hl, -hl, 0]]

    relative_pose = get_camera_pose(corners, square)
    rel_R, rel_pos = relative_pose
    print(rel_pos)
    cam_R, cam_pos = camera_pose
    # print(cam_R)

    middle = (0, 0, 0)
    middle -= rel_pos
    print("mid:", middle)
    print(np.linalg.inv(rel_R))
    middle = middle @ np.linalg.inv(rel_R)
    print("mid:", middle)
    middle = middle @ cam_R
    middle += cam_pos
    return middle