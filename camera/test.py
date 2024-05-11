from calibrate_camera import undistort_image
from object_detection import detect_object, detect_all
from cv_utilities import draw_image_objects
from transformations import get_img_center
import numpy as np
import cv2

# UNDISTORT TEST

# img = cv2.imread('test.jpg')
# print(img.shape)
# img = undistort_image(img)
# cv2.imwrite('und.jpg', img)



# OBJECT DETECTION full pipeline TEST
paths = [
    # "test/phone/easy1.png",
    # "test/phone/easy2.png",
    # "test/phone/easy3.png",
    # "test/phone/easy4.png",
    # "test/phone/med1.png",
    # "test/phone/med2.png",
    "test/phone/med3.png",
    # "test/phone/hard1.png",
    "test/phone/weird1.png",
]

# for path in paths:
#     results = detect_all(path)
#     draw_image_objects(path, results)



# OBJECT LOCALIZATION TEST
path = "test/phone/med3.png"
results = detect_all(path)
for r in results:
    if r["found"]:
        print("location of", r["path"], "is:", get_img_center(r["corners"], (np.diag([1,1,1]), [1, 2, 3])))
