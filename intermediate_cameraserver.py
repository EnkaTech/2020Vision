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
        cnt2 = contours[1]
    except IndexError:
        return img
    #Targetları dikdörtgen içine al
    rect1 = cv2.minAreaRect(cnt1)
    box_p1 = cv2.boxPoints(rect1)
    box1 = np.int0(box_p1)
    rect2 = cv2.minAreaRect(cnt2)
    box_p2 = cv2.boxPoints(rect2)
    box2 = np.int0(box_p2)
    cv2.drawContours(img,[box1],0,(0,0,255),2)
    cv2.drawContours(img,[box2],0,(0,0,255),2)
    return img

def cnt_test(cnt):
    rect = cv2.minAreaRect(cnt)
    width  = min(rect[1][0], rect[1][1])
    height = max(rect[1][0], rect[1][1])
    ratio = width/height
    if cv2.contourArea(cnt) > 200 and ratio > 0.35 and ratio < 0.6:
        return True
    else:
        return False

def maap(x, in_min,  in_max,  out_min,  out_max): 
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def calculate_errors(contours):
    try:
        cnt1 = contours[0]
        cnt2 = contours[1]
    except IndexError:
        return False, 0, 0
    #Target etrafında dikdörtgensel bölge oluştur
    rect1 = cv2.minAreaRect(cnt1)
    box_p1 = cv2.boxPoints(rect1)
    box1 = np.int0(box_p1)

    rect2 = cv2.minAreaRect(cnt2)
    box_p2 = cv2.boxPoints(rect2)
    box2 = np.int0(box_p2)

    #Targetların ağırlık merkezini bul
    M1 = cv2.moments(box1)
    M2 = cv2.moments(box2)
    center1 = int(M1['m10']/M1['m00'])
    center2 = int(M2['m10']/M2['m00'])

    #TODO z ekseninde hata hesabı
    z_error = 0
    #Targetların ekran merkezine olan uzaklığı arasındaki fark -> Y eksenindeki hata
    y_error = (240-center1) + (240-center2)
    return True, z_error, y_error

def main():
    cs = CameraServer.getInstance()
    cs.enableLogging()

    camera = cs.startAutomaticCapture()

    camera.setResolution(640, 480)

    proc_table = NetworkTables.getTable("imgproc")

    # Get a CvSink. This will capture images from the camera
    cvSink = cs.getVideo()

    # (optional) Setup a CvSource. This will send images back to the Dashboard
    outputStream = cs.putVideo("Result", 640, 480)

    # Allocating new images is very expensive, always try to preallocate
    img = np.zeros(shape=(480, 640, 3), dtype=np.uint8)

    while True:
        # Tell the CvSink to grab a frame from the camera and put it
        # in the source image.  If there is an error notify the output.
        time, img = cvSink.grabFrame(img)
        if time == 0:
            # Send the output the error.
            outputStream.notifyError(cvSink.getError())
            # skip the rest of the current iteration
            continue

        # Put a rectangle on the image
        contours = detect_targets(img)
        goodContours = list(filter(cnt_test, contours))
        if len(goodContours) >= 2:
            result = rectangle(img, goodContours)
            #success, r_error, h_error = calculate_errors(goodContours)

            # Sonuçları robota bildir
            proc_table.putBoolean('Target algılandı', True)
            #proc_table.putNumber('Heading', r_error)
            #proc_table.putNumber('Horizontal error', h_error)
        else:
            result = img
            proc_table.putBoolean('Target algılandı', False)
            proc_table.putNumber('Heading', 0)
            proc_table.putNumber('Horizontal error', 0)
        

        # Give the output stream a new image to display
        outputStream.putFrame(result)


if __name__ == "__main__":

    # To see messages from networktables, you must setup logging
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # You should uncomment these to connect to the RoboRIO
    from networktables import NetworkTables
    NetworkTables.initialize()

    main()
