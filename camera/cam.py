#!/usr/bin/python3

import cv2
import argparse
import threading
import time

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
    cap = cv2.VideoCapture(0, cv2.CAP_V4L)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[0])
    ret, frame = cap.read()
    cap.release()
    return frame

def output_clr_image(path):
    img = capture_image()
    cv2.imwrite(path, img)

def output_bw_image(path):
    img = capture_image()
    bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(path, bw)

def interval(num, interval, path, color=False):
    num = int(num)
    intr = None
    ctr = 0

    def cap():
        nonlocal ctr
        ctr += 1
        fpath = path.replace(".jpg", "")
        fpath = fpath + "_" + str(int(time.time())) + "_" + '{:05d}'.format(ctr) + ".jpg"
        if color:
            output_clr_image(fpath)
        else:
            output_bw_image(fpath)
        if ctr >= num:
            intr.cancel()

    intr = SetInterval(float(interval), cap)

def single(output, color):
    if color:
        output_clr_image(output)
    else:
        output_bw_image(output)

def main(args):
    if args.interval is not None:
        interval(args.interval[1], args.interval[0], args.output, args.color)
    else:
        single(args.output, args.color)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Output path of the captured image", required=True, type=str)
    parser.add_argument("--color", help="Output image in color", action="store_true")
    parser.add_argument("--interval", help="Cap interval (sec) (n) times", nargs=2)
    args = parser.parse_args()
    main(args)
