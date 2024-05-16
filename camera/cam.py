#!/usr/bin/python3

import cv2
import argparse
import threading
import time
import os
import json
from pymavlink import mavutil

class SetInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()

def capture_image(resolution=(1920, 1080)):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    ret, frame = cap.read()
    cap.release()
    return frame

def save_image(path, color=False, data=None):
    img = capture_image()
    if not color:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(path, img)
    
    # Create a JSON object with image metadata
    json_data = {
        'image_path': path,
        'timestamp': int(time.time()),
        #'gps_data': gps_data,
        #'imu_data': imu_data
        "data": data
    }
    
    # Save the JSON object to a file with the same name as the image
    json_path = f"{os.path.splitext(path)[0]}.json"
    with open(json_path, 'w') as json_file:
        json.dump(json_data, json_file)
        
    print(json_data, "\n\n\n")

def get_pixhawk_data(master):
    try:
        gps_data = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
        #pos_data = master.recv_match(type='LOCAL_POSITION_NED', blocking=True, timeout=1)
        imu_data = master.recv_match(type='SCALED_IMU2', blocking=True, timeout=1)
        att_data = master.recv_match(type='ATTITUDE', blocking=True, timeout=1)
        #gps_data = master.messages['GLOBAL_POSITION_INT']
        #gps_data = master.messages['SCALED_IMU2']
        #gps_data = master.messages['ATTITUDE']

        #print(gps_data)
        #print(pos_data)
        #print(imu_data)
        #print(att_data)
        
        data = {
            "gps_data": gps_data.to_dict(),
            #"pos_data": pos_data.to_dict(),
            "imu_data": imu_data.to_dict(),
            "att_data": att_data.to_dict(),
        }
        return data
    except Exception as e:
        print(e)
        return None

def interval_capture(num, interval, path, color=False, pixhawk_url=None):
    master = None
    if pixhawk_url:
        master = mavutil.mavlink_connection(pixhawk_url, baud = 57600)

    intr = None
    ctr = 0

    def capture():
        nonlocal ctr
        ctr += 1
        timestamp = int(time.time())
        fpath = f"{os.path.splitext(path)[0]}_{timestamp}_{ctr:05d}.jpg"
        
        #gps_data, imu_data = get_pixhawk_data(master) if master else (None, None)
        data = get_pixhawk_data(master) if master else (None, None)
        #save_image(fpath, color, gps_data, imu_data)
        save_image(fpath, color, data)
        #print(gps_data)
        
        if ctr >= num:
            intr.cancel()

    intr = SetInterval(interval, capture)

def main(args):
    if args.interval is not None:
        interval_capture(int(args.interval[1]), float(args.interval[0]), args.output, args.color, args.pixhawk_url)
    else:
        master = mavutil.mavlink_connection(args.pixhawk_url, baud = 57600) if args.pixhawk_url else None
        data = get_pixhawk_data(master) if master else (None, None)
        save_image(args.output, args.color, data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Output path of the captured image", required=True, type=str)
    parser.add_argument("--color", help="Output image in color", action="store_true")
    parser.add_argument("--interval", help="Capture interval (sec) (n) times", nargs=2)
    parser.add_argument("--pixhawk_url", help="Pixhawk connection URL (e.g., tcp:127.0.0.1:5760)", type=str)
    args = parser.parse_args()
    main(args)
