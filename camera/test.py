from calibrate_camera import undistort_image
import cv2

img = cv2.imread('test.jpg')
print(img.shape)
img = undistort_image(img)
cv2.imwrite('und.jpg', img)