import cv2
import numpy as np
from cv_utilities import load_camera_image, normalize_corners

# Debugging and visualizing functions
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

def draw_image_corners(img, corners1, corners2=[], corners3=[]):
    import copy
    img = copy.copy(img)
    # color_img = load_camera_image(img_path, True)
    for c in normalize_corners(corners1):
        img = cv2.circle(img, (int(c[0]), int(c[1])), radius=10, color=(0, 0, 255), thickness=-10)
    for c in normalize_corners(corners2):
        img = cv2.circle(img, (int(c[0]), int(c[1])), radius=5, color=(255, 0, 0), thickness=-5)
    for c in normalize_corners(corners3):
        img = cv2.circle(img, (int(c[0]), int(c[1])), radius=3, color=(0, 255, 0), thickness=-3)

    cv2.imshow("Result", cv2.resize(img, (800, 600)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()