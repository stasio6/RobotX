import cv2
import time_utils
import time
import autopilot as ap
from os.path import join
import json

class SensorReader():
    def __init__(self, read_freq):
        self.read_freq = read_freq
        self.init_sensors()
    

    def init_sensors(self):
        self.camera_resolution = (1920, 1080)
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_resolution[0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_resolution[1])
        self.camera = camera

        self.apm = ap.Autopilot(ap.SERIAL_PORT, ap.DEFAULT_BAUD_RATE)

    def read_sensors(self, output_dir):
        timestamp = time_utils.get_timestamp(millis=True)
        ret, image = self.camera.read() 
        if not ret:
            image = None
        ap_data = self.apm.get_data() 

        image_path = join(output_dir, f"{timestamp}_cam.jpg")
        cv2.imwrite(image_path, image)

        sensor_data_path = join(output_dir, f"{timestamp}_sensors.json")
        sensor_data = {
            "image_path": image_path,
            "gps": ap_data["gps"],
            "imu": ap_data["imu"],
            "att": ap_data["attitude"]
        }
        with open(sensor_data_path, "w") as f:
            json.dump(sensor_data, f, indent=4)

        sensor_data["image"] = image
        return sensor_data

if __name__ == "__main__":
    reader = SensorReader(10)
    temp_path = "temp"
    reader.read_sensors(temp_path)