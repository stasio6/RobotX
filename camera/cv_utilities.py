import cv2
import numpy as np
from calibrate_camera import undistort_image

def load_target_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE) # TODO: Don't read it from file
    img = cv2.resize(img, (800, 800)) # TODO: Maybe remove the resizing?
    return img

def load_camera_image(path, useColor=False):
    color = cv2.IMREAD_COLOR if useColor else cv2.IMREAD_GRAYSCALE
    camera_image = cv2.imread(path, color)
    # camera_image = undistort_image(camera_image)
    return camera_image

def prepare_target_images(target_images, calculate_key_descriptors):
    for target_image in target_images:
        target_image["image"] = load_target_image(target_image["path"])
        target_image["descriptors"] = calculate_key_descriptors(target_image["image"])
    return target_images

def get_corners(img, camera_image_path=None):
    # print(img)
    # cv2.imshow("Shapes", cv2.resize(img, (800, 600)))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    corners = cv2.goodFeaturesToTrack(img, 800, 0.01, 30)
    corners = corners_to_subpix2(img, corners)
    # draw_image_corners(img, corners)

    return corners

def corners_to_subpix2(img, corners):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), criteria)
    return corners

def get_closest_corners(img, targets, corners):
    res = []
    max_dist = 30
    for t in targets:
        best = (max_dist, t)
        for c in corners:
            if np.linalg.norm(c - t) < best[0]:
                best = (np.linalg.norm(c - t), c[0])
        res.append(best[1])
    return res

def draw_image_objects(img_path, results):
    color_img = load_camera_image(img_path, True)
    for r in results:
        if not r['found']:
            continue
        corners = r['corners']
        num = 0
        for c in corners:
            color_img = cv2.circle(color_img, (int(c[0]), int(c[1])), radius=5, color=(0, 0, 255), thickness=-5)
            cv2.putText(color_img, str(num), (int(c[0]), int(c[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            num += 1
        color_img = cv2.polylines(color_img, [np.array(corners, dtype=int).reshape((-1, 1, 2))], isClosed=True, color=(255, 0, 0), thickness=1)
        cv2.putText(color_img, r['name'], (int(corners[0][0]), int(corners[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.imshow("Result", cv2.resize(color_img, (800, 600)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def draw_image_corners(img, corners):
    import copy
    img = copy.copy(img)
    # color_img = load_camera_image(img_path, True)
    for c in corners:
        import collections
        if isinstance([1, 2, 3], (collections.abc.Sequence, np.ndarray)):
            c = c[0]
        img = cv2.circle(img, (int(c[0]), int(c[1])), radius=5, color=(0, 0, 255), thickness=-5)
    # color_img = cv2.polylines(color_img, [np.array(corners, dtype=int).reshape((-1, 1, 2))], isClosed=True, color=(255, 0, 0), thickness=1)
    # cv2.putText(color_img, r['name'], (int(corners[0][0]), int(corners[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Result", cv2.resize(img, (800, 600)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

