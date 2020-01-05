#!/usr/bin/env python3
#
# This is a demo program showing CameraServer usage with OpenCV to do image
# processing. The image is acquired from the USB camera, then a rectangle
# is put on the image and sent to the dashboard. OpenCV has many methods
# for different types of processing.
#
# Warning: If you're using this with a python-based robot, do not run this
# in the same program as your robot code!
#

import cv2
import numpy as np
import math  
from cscore import CameraServer

def detect_targets(capture):
    #Bir kare al
    # Gürültü kaldırma için gerekli kerneller
    kernel = np.ones((9,9),np.uint8)
    kernel2 = np.ones((13,13),np.uint8)
    # Beyazlık filtresi
    gray = cv2.cvtColor(capture, cv2.COLOR_BGR2GRAY)
    _, filter1 = cv2.threshold(gray,240,255,cv2.THRESH_BINARY)
    # Arkaplandaki beyaz noktaları ve cisim üzerindeki siyah noktaları yok et
    filter2 = cv2.morphologyEx(filter1, cv2.MORPH_OPEN, kernel)
    filter3 = cv2.morphologyEx(filter2, cv2.MORPH_CLOSE, kernel2)
    #Kontur bul
    _, contours, _ = cv2.findContours(filter3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

def rectangle(img, contours):
    try:
        cnt1 = contours[0]
    except IndexError:
        return img
    #Targetları dikdörtgen içine al
    rect1 = cv2.minAreaRect(cnt1)
    box_p1 = cv2.boxPoints(rect1)
    box1 = np.int0(box_p1)
    cv2.drawContours(img,[box1],0,(0,0,255),2)
    return img

def cnt_test(cnt):
    rect = cv2.minAreaRect(cnt)
    width  = min(rect[1][0], rect[1][1])
    height = max(rect[1][0], rect[1][1])
    ratio = width/height
    if cv2.contourArea(cnt) > 200 and ratio > 0.35 and ratio < 1.2:
        return True
    else:
        return False

def calculate_errors(contours):
    try:
        cnt1 = contours[0]
    except IndexError:
        return False, 0
    #Target etrafında dikdörtgensel bölge oluştur
    rect1 = cv2.minAreaRect(cnt1)
    box_p1 = cv2.boxPoints(rect1)
    box1 = np.int0(box_p1)

    #Targetların ağırlık merkezini bul
    M1 = cv2.moments(box1)
    M2 = cv2.moments(box2)
    center1x = int(M1['m10']/M1['m00'])
    center1y = int(M1["m01"] / M1["m00"])
    #Targetların ekran merkezine olan uzaklığı arasındaki fark -> Y eksenindeki hata
    cameraheight = 40
    targetheight = 300
    cameraangle = 10
    targetangle = (180 - center1y) / 180 * 43.30
    distance = (targetheight-cameraheight)/ math.tan(cameraangle+targetangle)
    #further code will be added
    y_error = 320 - center1x
    
    return True, y_error,distance

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

        # Put a rectangle on the image
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
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # You should uncomment these to connect to the RoboRIO
    from networktables import NetworkTables
    NetworkTables.initialize()

    main()
