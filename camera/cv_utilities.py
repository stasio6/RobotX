import cv2
import numpy as np

def get_corners(img, camera_image_path=None):
    # print(img)
    # cv2.imshow("Shapes", cv2.resize(img, (800, 600)))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # kernel = np.ones((7, 7), np.uint8) 
    # closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=1)
    # smooth = cv2.smooth(img, smooth, cv2.CV_BLUR, 9, 9, 2, 2); 
    # blur = cv2.GaussianBlur(img,(5,5),0)
    # cv2.imshow("Shapes", cv2.resize(blur, (800, 600)))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # ret,thresh = cv2.threshold(closing,128,255,cv2.THRESH_BINARY)
    # thresh = cv2.adaptiveThreshold(closing, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2)
    # cv2.imshow("Shapes", cv2.resize(img, (800, 600)))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    corners1 = cv2.cornerHarris(img,2,7,0.04)
    corners2 = cv2.cornerMinEigenVal(img, 7, 3)
    corners3 = cv2.goodFeaturesToTrack(img, 800, 0.01, 30)
    corners4 = cv2.goodFeaturesToTrack(img, 100, 0.01, 30, useHarrisDetector=True)
    # print(corners3)
    corners1 = corners_to_subpix(img, corners1)
    corners2 = corners_to_subpix(img, corners2)
    corners3 = corners_to_subpix2(img, corners3)
    corners4 = corners_to_subpix2(img, corners4)

    # Method choice
    corners = corners3 # This works the best
    
    # draw_image_corners(img, corners)
    # draw_image_corners(img, corners4)
    # for c in corners:
        # img = cv2.circle(img, (c[0],c[1]), radius=10, color=(0, 255, 0), thickness=-10)
    # cv2.imshow("Shapes", cv2.resize(img, (800, 600)))
    # cv2.waitKey(0)
    return corners

def corners_to_subpix2(img, corners):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), criteria)
    return corners

def corners_to_subpix(img, corners):
    dst = cv2.dilate(corners,None)
    th = 0.001
    ret, dst = cv2.threshold(dst,th*dst.max(),255,0)
    dst = np.uint8(dst)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst) # TODO: Maybe??? Check if better accuracy
    corners = centroids
    # draw_image_corners(img, corners)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    # print("Centroids")
    # print(centroids)
    corners = cv2.cornerSubPix(img, np.float32(centroids), (5, 5), (-1, -1), criteria)
    return corners

# Inspired by https://docs.opencv.org/4.x/dc/d0d/tutorial_py_features_harris.html
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
    color_img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    for r in results:
        if not r['found']:
            continue
        corners = r['corners']
        for c in corners:
            color_img = cv2.circle(color_img, (int(c[0]), int(c[1])), radius=10, color=(0, 0, 255), thickness=-10)
        color_img = cv2.polylines(color_img, [np.array(corners, dtype=int).reshape((-1, 1, 2))], isClosed=True, color=(255, 0, 0), thickness=1)
        cv2.putText(color_img, r['path'].split('/')[-1], (int(corners[0][0]), int(corners[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.imshow("Result", cv2.resize(color_img, (800, 600)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def draw_image_corners(img, corners):
    # img = cv2.imread(img, cv2.IMREAD_COLOR)
    for c in corners:
        import collections
        if isinstance([1, 2, 3], (collections.abc.Sequence, np.ndarray)):
            c = c[0]
        img = cv2.circle(img, (int(c[0]), int(c[1])), radius=10, color=(0, 0, 255), thickness=-10)
    # color_img = cv2.polylines(color_img, [np.array(corners, dtype=int).reshape((-1, 1, 2))], isClosed=True, color=(255, 0, 0), thickness=1)
    # cv2.putText(color_img, r['path'].split('/')[-1], (int(corners[0][0]), int(corners[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Result", cv2.resize(img, (800, 600)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

