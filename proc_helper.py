import cv2
import numpy as np
import math



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

    return True, y_error, distance
