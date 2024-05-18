from collections import defaultdict
import numpy as np
locations = defaultdict(list)

def aggregate_results(detected_objects):
    results = {}
    for detected_object in detected_objects:
        name = detected_object["name"]
        if detected_object["found"]:
            locations[name].append(detected_object["real_world_pos"])
        if len(locations[name]) > 0:
            mean = np.mean(np.array(locations[name]), axis=0)
            results[name] = mean
    return results
