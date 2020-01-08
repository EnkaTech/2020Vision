#!/usr/bin/env python3

import cv2
import numpy as np
import math
import logging
from cscore import CameraServer
from networktables import NetworkTables
from proc_helper import *

def main():
    cs = CameraServer.getInstance()
    cs.enableLogging()

    camera = cs.startAutomaticCapture()

    camera.setResolution(640, 360)

    proc_table = NetworkTables.getTable("imgproc")

    # Get a CvSink. This will capture images from the camera
    cvSink = cs.getVideo()

    # (optional) Setup a CvSource. This will send images back to the Dashboard
    outputStream = cs.putVideo("LQimg", 120, 90)

    # Allocating new images is very expensive, always try to preallocate
    imgHQ = np.zeros(shape=(640, 360, 3), dtype=np.uint8)
    imgLQ = np.zeros(shape=(120, 90, 3), dtype=np.uint8)
    while True:
        # Tell the CvSink to grab a frame from the camera and put it
        # in the source image.  If there is an error notify the output.
        time, processingimg = cvSink.grabFrame(imgHQ)
        _, dashboardimg =  cvSink.grabFrame(imgLQ)
        if time == 0:
            # Send the output the error.
            outputStream.notifyError(cvSink.getError())
            # skip the rest of the current iteration
            continue

        # Find suitable contours
        contours = detect_targets(processingimg)
        goodContours = list(filter(cnt_test, contours))
        if len(goodContours) >= 1:
            rectangledresult = rectangle(dashboardimg, goodContours)        
            success, y_error,distance = calculate_errors(goodContours)
            # Sonuçları robota bildir
            proc_table.putBoolean('Target algılandı', True)    
            proc_table.putNumber('Horizontal error', y_error)
            proc_table.putNumber('Horizontal error', distance)
        else:
            proc_table.putBoolean('Target algılandı', False)
            proc_table.putNumber('Horizontal error', 0)
        

        # Give the output stream a new image to display
        outputStream.putFrame(rectangledresult)


if __name__ == "__main__":

    # To see messages from networktables, you must setup logging


    logging.basicConfig(level=logging.DEBUG)

    # Create a new NetworkTables instance on the network

    NetworkTables.initialize()

    main()
