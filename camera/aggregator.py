from collections import defaultdict
import numpy as np
from gps_utils import calculate_distance

AGGREGATOR_RANSAC_TOLERANCE = 15

locations = defaultdict(list)

def lonlat_error(pt1, pt2):
    return calculate_distance(pt1[0], pt1[1], pt2[0], pt2[1])

def RANSAC(points, error_fun=lonlat_error, tolerance=AGGREGATOR_RANSAC_TOLERANCE):
    best = (0, 0)
    for candidate in points:
        inliers = 0
        for pt in points:
            if error_fun(candidate, pt) <= tolerance:
                inliers += 1
        if inliers > best[1]:
            best = (pt, inliers)

    return list(filter(lambda pt : error_fun(best[0], pt) <= tolerance, points))

def aggregate_results(detected_objects):
    results = {}
    for detected_object in detected_objects:
        name = detected_object["name"]
        if detected_object["found"]:
            locations[name].append(detected_object["real_world_pos"])
        if len(locations[name]) > 0:
            inliers = RANSAC(locations[name])
            mean = np.mean(np.array(inliers), axis=0)
            results[name] = {"result": mean, "inliers": len(inliers)}
            # print(name, ' '.join(["%.2f" % s for s in mean]))
    return results
