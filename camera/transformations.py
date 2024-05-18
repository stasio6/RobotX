import cv2
import numpy as np
from calibrate_camera import load_coefficients
from scipy.spatial.transform import Rotation

def get_relative_camera_pose(corners, square):
    camera_matrix, dist_matrix = load_coefficients()
    print(corners)
    print(square)
    print(camera_matrix)
    success, rvec, tvec = cv2.solvePnP(np.array(square), np.array(corners), camera_matrix, None, flags=cv2.SOLVEPNP_IPPE_SQUARE)
    if not success:
        print("SMUTACZ!")
    R = cv2.Rodrigues(rvec)[0]
    print("OUT:", success, rvec, tvec)
    print(R)
    return R, tvec.reshape(-1)

def get_camera_R(imu):
    roll = imu["roll"]
    pitch = imu["pitch"]
    yaw = imu["yaw"]
    yaw = 0 # TODO: Remove, just for testing
    # print("roll:", roll, "pitch:", pitch, "yaw:", yaw)
    # print(Rotation.from_euler("XYZ", (roll, pitch, yaw), degrees=False).as_matrix())
    # print("\n")
    return Rotation.from_euler("XYZ", (roll, pitch, yaw), degrees=False).as_matrix()

def parse_gps(gps):
    return gps["lat"], gps["lon"], gps["alt"]

def get_img_center(corners, lat, lon, alt, cam_R, object_side=150):
    hl = object_side/2
    square = [[-hl, hl, 0], [hl, hl, 0], [hl, -hl, 0], [-hl, -hl, 0]]

    rel_R, rel_pos = get_relative_camera_pose(corners, square)
    print("Relative camera pos", rel_pos)
    # Normalize roll pitch roll to assume camera is looking down
    roll,pitch,yaw = Rotation.from_matrix(rel_R).as_euler('xyz', degrees=True)
    roll += 180
    # yaw *= -1
    rel_R = Rotation.from_euler("XYZ", (roll, pitch, yaw), degrees=True).as_matrix()
    print("Relative rot", Rotation.from_matrix(rel_R).as_euler('xyz', degrees=True))
    # print(cam_R)

    middle = (0, 0, 0)
    middle -= rel_pos
    print("mid:", middle)
    print(np.linalg.inv(rel_R))
    middle = middle @ np.linalg.inv(rel_R)
    print("mid:", middle)
    print("cam_R", cam_R)
    middle = middle @ cam_R
    print("result:", middle)
    return middle # TODO: Remove

    # TODO: Take into account camera-GPS offset
    lon += middle[0] # TODO: Use gps add
    lat -= middle[1] # TODO: Use gps add
    alt -= middle[2]
    return (lon, lat, alt)

def localize_objects(metadata, detected_objects):
    lat, lon, alt = parse_gps(metadata["gps_data"])
    cam_R = get_camera_R(metadata["att_data"])
    for detected_object in detected_objects:
        if not detected_object["found"]:
            continue
        detected_object["real_world_pos"] = get_img_center(detected_object["corners"], lat, lon, alt, cam_R)
    return detected_objects
