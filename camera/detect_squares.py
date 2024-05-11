import cv2
import numpy as np
from cv_utilities import get_closest_corners, get_corners

img = cv2.imread('test/cse/img1.jpg', cv2.IMREAD_COLOR)
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.imread('test/cse/img1.jpg', cv2.IMREAD_GRAYSCALE)
# TODO: Denoising

kernel = np.ones((7, 7), np.uint8) 
closing = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel, iterations=1) 
ret,thresh = cv2.threshold(closing,170,255,cv2.THRESH_BINARY)
contours,hierarchy = cv2.findContours(thresh, 1, 2)
print("Number of contours detected:", len(contours))
subpixel_corners = get_corners(gray)

for cnt in contours:
   x1,y1 = cnt[0][0]
   approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
   if len(approx) == 4:
      x, y, w, h = cv2.boundingRect(cnt)
      if w < 50 or h < 50:
         continue
      # print(w, h)
      ratio = float(w)/h
      if ratio >= 0.9 and ratio <= 1.1:
         img = cv2.drawContours(img, [cnt], -1, (0,255,255), 3)
         cv2.putText(img, 'Square', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
      else:
         cv2.putText(img, 'Rectangle', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
         img = cv2.drawContours(img, [cnt], -1, (0,255,0), 3)
      
      rect_corners = [approx[0][0], approx[1][0], approx[2][0], approx[3][0]]
      # print(rect_corners)
      for c in rect_corners:
         img = cv2.circle(img, (c[0],c[1]), radius=10, color=(0, 255, 0), thickness=-10)
      best_corners = get_closest_corners(gray, rect_corners, subpixel_corners)
      # print(best_corners)
      for c in best_corners:
         img = cv2.circle(img, (c[0],c[1]), radius=10, color=(0, 0, 255), thickness=-10)

# cv2.imshow("Greyscale", cv2.resize(closing, (800, 600)))
# cv2.waitKey(0)
# cv2.imshow("Threshold", cv2.resize(thresh, (800, 600)))
# cv2.waitKey(0)
cv2.imshow("Shapes", cv2.resize(img, (800, 600)))
cv2.waitKey(0)
cv2.destroyAllWindows()
