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

    procTable = NetworkTables.getTable("imgproc")

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
        time, processingImg = cvSink.grabFrame(imgHQ)
        if time == 0:
            # Send the output the error.
            outputStream.notifyError(cvSink.getError())
            logging.debug(cvSink.getError())
            # skip the rest of the current iteration
            continue

        # Find suitable contours
        contours = detectTargets(processingImg)
        goodContours = list(filter(cntTest, contours))
        if len(goodContours) >= 1:
            rectangledResult = rectangle(processingImg, goodContours)        
            success, yError,distance = calculateErrors(goodContours)
            # Sonuçları robota bildir
            procTable.putBoolean('Target algılandı', True)    
            procTable.putNumber('Horizontal error', yError)
            procTable.putNumber('Distance', distance)
        else:
            rectangledResult = processingImg
            procTable.putBoolean('Target algılandı', False)
            procTable.putNumber('Horizontal error', 0)

        imgLQ = cv2.resize(rectangledResult, (120, 90))

        # Give the output stream a new image to display
        outputStream.putFrame(imgLQ)


if __name__ == "__main__":

    # To see messages from networktables, you must setup logging


    logging.basicConfig(filename="/tmp/vision.log", level=logging.DEBUG)

    # Create a new NetworkTables instance on the network

    NetworkTables.initialize()

    main()
