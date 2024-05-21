import numpy as np
import os, re
import pickle
import json
import cv2

def unndarray(d):
  if isinstance(d, np.generic):
    return float(d)
  if isinstance(d, np.ndarray):
    d = list(d)
  if isinstance(d, list):
    res = []
    for i in range(len(d)):
      res.append(unndarray(d[i]))
    return res
  if not isinstance(d, dict):
    return d
  for key in d:
    d[key] = unndarray(d[key])    
  return d

def save_capture_data(json_path, localization_data, aggregation_data):
    json_data = {
        "localization": localization_data,
        "aggregation": aggregation_data
    }
    json_data = unndarray(json_data)
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file)

def save_json_data(json_path, image_path, image, metadata):
    json_data = {
            "path": image_path, 
            "gps": metadata["gps_data"],
            "imu": metadata["imu_data"],
            "att": metadata["att_data"],
        }
    print("Saving image to path:", image_path)
    if image is None:
        print("IMG NONE")
    cv2.imwrite(image_path, image)
    print("Saving JSON to path:", json_path)
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file)
    json_data["image"] = image
    return json_data

def read_test_data(iter_count, test_directory):
    def find_file(ending):
        regex = re.compile('.*' + ending)
        for root, dirs, files in os.walk(test_directory):
            for file in files:
                if regex.match(file):
                    return file
    image_path = test_directory + '/captures/' + find_file('{:05d}.jpg'.format(iter_count))
    json_path = test_directory + '/json/' + find_file('{:05d}.json'.format(iter_count))
    with open(json_path, "r") as json_file:
        image_data = json.load(json_file)
    print(image_data)
    image_data["image"] = cv2.imread(image_path, cv2.IMREAD_COLOR)
    image_data["image_path"] = image_path
    metadata = {
        "gps_data": image_data["gps"],
        "att_data": image_data["att"]
    }
    return metadata, image_data

def serialize_keypoints(keypoints):
    res = []
    for point, desc in zip(keypoints[0], keypoints[1]):
        res.append((point.pt, point.size, point.angle, point.response, point.octave, point.class_id, desc))
    return res

def deserialize_keypoints(keypoints):
    keypoint = []
    descriptors = []
    for point in keypoints:
        print(point)
        keypoints.append(cv2.KeyPoint(x=point[0][0],y=point[0][1],size=point[1], angle=point[2], response=point[3], octave=point[4], class_id=point[5]))
        descriptors.append(point[6])
    return (keypoints, descriptors)

def save_target_images_pickle(path, images):
    for image in images:
        image["descriptors"] = serialize_keypoints(image["descriptors"])
    with open(path, "wb") as file:
        pickle.dump(images, file)

def load_target_images_pickle(path):
    with open(path, "rb") as file:
        images = pickle.load(file)
    for image in images:
        image["descriptors"] = deserialize_keypoints(image["descriptors"])