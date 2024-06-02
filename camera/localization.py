import cv2
import numpy as np
from calibrate_camera import load_coefficients
from scipy.spatial.transform import Rotation
from gps_utils import add_distance_to_coordinates

DEFAULT_OBJECT_SIZE = 150

def get_relative_camera_pose(corners, square):
    camera_matrix, dist_matrix = load_coefficients()
    success, rvec, tvec = cv2.solvePnP(np.array(square), np.array(corners), camera_matrix, dist_matrix, flags=cv2.SOLVEPNP_IPPE_SQUARE)
    if not success:
        raise Exception("PnP not successful")

    # R = cv2.Rodrigues(rvec)[0]
    return tvec.reshape(-1)

def get_camera_R(imu):
    roll = imu["roll"]
    pitch = imu["pitch"]
    yaw = imu["yaw"]
    return Rotation.from_euler("XYZ", (roll, pitch, yaw), degrees=False).as_matrix()

def parse_gps(gps):
    return gps["lat"], gps["lon"], gps["alt"]

def get_img_center(corners, lat, lon, alt, cam_R, object_side=DEFAULT_OBJECT_SIZE):
    hl = object_side/2
    square = [[-hl, hl, 0], [hl, hl, 0], [hl, -hl, 0], [-hl, -hl, 0]]

    middle = get_relative_camera_pose(corners, square)
    middle = cam_R @ middle

    lat, lon = add_distance_to_coordinates(lat, lon, -middle[1]/100, middle[0]/100)
    alt -= middle[2]/1000
    return (lat, lon, alt)

def localize_objects(metadata, detected_objects):
    lat, lon, alt = parse_gps(metadata["gps"])
    cam_R = get_camera_R(metadata["attitude"])
    for detected_object in detected_objects:
        if not detected_object["found"]:
            detected_object["real_world_pos"] = None
            continue
        try:
            detected_object["real_world_pos"] = get_img_center(detected_object["corners"], lat, lon, alt, cam_R)
        except:
            detected_object["found"] = False
            detected_object["real_world_pos"] = None
            print("Object localization failed - invalid object detected")
    return detected_objects
