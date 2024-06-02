import os
import json

import cv2

import capture as cap
import object_detection as od
import localization as loc
import aggregator as aggr
import file_utils as fu
import time_utils as tu

class Localizer():
    def __init__(self, sr, target_ids, save_dir):
        self.sensor_reader = sr
        self.targets = target_ids
        self.save_dir = save_dir
        self.preprocess_targets()

    def preprocess_targets(self):
        for target in self.targets:
            img = cv2.imread(target["path"], cv2.IMREAD_GRAYSCALE) 
            target["image"] = img
            target["image_shape"] = img.shape
            target["descriptors"] = od.calculate_key_descriptors(img)
            print(f"{target['name']}, dims {img.shape}")

    def localize(self, image_data):
        detected_objects = od.detect_all_targets(image_data, self.targets)
        object_locations = loc.localize_objects(image_data, detected_objects)
        aggregate_data = aggr.aggregate_results(object_locations)

        timestamp = tu.get_timestamp(millis=True)
        save_data = {
            "timestamp" : timestamp,
            "localization": object_locations,
            "aggregation": aggregate_data
        }
        data_serial = fu.unndarray(save_data)

        data_path = os.path.join(self.save_dir, f"{timestamp}_aggr.json")
        with open(data_path, "w") as f:
            json.dump(data_serial, f, indent=4)
        
        return save_data

    def localize_loop(self):
        while True:
            image_data = self.sensor_reader.read_sensors()
            loc_data = self.localize(image_data)
            print(f"[{loc_data['timestamp']}]")
            for entry in loc_data["localization"]:
                print(f"{entry['name']}: found {entry['found']} at {entry['real_world_pos']}")
            print()
        
    def localize_test(self):
        image_data = self.sensor_reader.read_sensors()
        loc_data = self.localize(image_data)

if __name__ == "__main__":
    save_dir = fu.new_save_dir()

    sensor_reader = cap.SensorReader(save_dir)
    target_ids = [
        {
            "name": "target_n",
            "path": "targets/target_n_small.jpg"
        },
        {
            "name": "target_r",
            "path": "targets/target_r_small.jpg"
        }
    ]
    lc = Localizer(sensor_reader, target_ids, save_dir)
    lc.localize_loop()
