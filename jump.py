import numpy as np
import sys
import os
import math
import cv2
os.system('adb devices')
currpath = sys.path[0]
print(currpath)
times = int(input())  # how many times you jump
for i in range(times):
    os.system('adb shell /system/bin/screencap -p /sdcard/0.png')
    os.system('adb pull /sdcard/0.png 0.png')
    a = cv2.imread('0.png')
    cv2.namedWindow('A')
    b = cv2.Canny(a, 55, 120)
    minLineLength = 200
    maxLineGap = 5
    lines = cv2.HoughLinesP(b, 1, 3.1416 / 180, 30,
                            minLineLength=30, maxLineGap=5)
    lines1 = lines[:, 0, :]
    x1s, y1s = 0, 0
    height = len(b)
    width = len(b[0])
    liner = [10, height, 2, height]
    linel = [10, height, 2, height]
    for x1, y1, x2, y2 in lines1:  # here x1 < x2
        cv2.line(b, (x1, y1), (x2, y2), (0, 0, 0), 3)
        if y1 != y2 and abs((x1 - x2) / (y1 - y2) - 1.72) < 0.03:  # \
            if y1 < liner[1]:
                liner = [x1, y1, x2, y2]
        elif y1 != y2 and abs((x1 - x2) / (y1 - y2) + 1.72) < 0.03:  # /
            if y2 < linel[3]:
                linel = [x1, y1, x2, y2]
    cv2.line(a, (liner[0], liner[1]), (liner[2], liner[3]), (100, 0, 0), 3)
    cv2.line(a, (linel[0], linel[1]), (linel[2], linel[3]), (100, 0, 0), 3)
    dist11 = math.hypot(linel[0] - liner[0], linel[1] - liner[1])
    dist12 = math.hypot(linel[0] - liner[2], linel[1] - liner[3])
    dist21 = math.hypot(linel[2] - liner[0], linel[3] - liner[1])
    dist22 = math.hypot(linel[2] - liner[2], linel[3] - liner[3])
    mindist = min(dist11, dist12, dist21, dist22)
    if dist11 == mindist:
        x1s = (linel[2] + liner[2]) / 2
        y1s = (linel[3] + liner[3]) / 2
    elif dist12 == mindist:
        x1s = (linel[2] + liner[0]) / 2
        y1s = (linel[3] + liner[1]) / 2
    elif dist21 == mindist:
        x1s = (linel[0] + liner[2]) / 2
        y1s = (linel[1] + liner[3]) / 2
    else:
        x1s = (linel[0] + liner[0]) / 2
        y1s = (linel[1] + liner[1]) / 2
    cv2.circle(a, (int(x1s), int(y1s)), 5, (0, 255, 255), 3)
    circles = cv2.HoughCircles(b, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=100, param2=22,
                               minRadius=25, maxRadius=35)
    circles = np.uint16(np.around(circles))  # find where the person is.
    x0, y0 = 0, 0
    for i in circles[0, :]:
        # draw the center of the circle
        cv2.circle(a, (i[0], i[1]), 2, (0, 0, 255), 3)
        # get its foot point
        cv2.circle(a, (i[0], i[1] + 165), 2, (0, 0, 255), 3)
        x0 = int(i[0])
        y0 = int(i[1] + 165)
        break
    if x0 > width / 2:  # find an oval that is x:y
        start = 0
        end = int(width / 2)
    else:
        start = int(width / 2)
        end = width
    breakall = 0
    null = [0, 0, 0, 0, 0, 0, 0, 0]
    x1o, y1o = 1002, 1999
    for y in range(700, height):
        if breakall == 1:
            break
        for x in range(start, end):
            if breakall == 1:
                break
            if b[y][x] != 0:
                p = 0
                for p in range(10, 200):
                    if y + p < height and b[y + p][x] != 0:
                        break
                if p != 199:
                    u = int(p * 0.867)
                    p2 = int(p / 2)
                    if x - u < 3 or x + u > width - 3:
                        continue
                    if b[y + p2][x - u - 3:x - u + 4] == null or b[y + p2][x + u - 3:x + u + 4] == null:
                        continue
                    breakall = 1
                    cv2.line(a, (x, y), (x, y + p), (0, 0, 128), 3)
                    cv2.line(a, (x - u, y + p2),
                             (x + u, y + p2), (0, 0, 128), 3)
                    x1o = x + 3
                    y1o = y + p2
    if y1s < y1o:
        res = math.hypot(x0 - x1s, y0 - y1s)
    else:
        res = math.hypot(x0 - x1o, y0 - y1o)
    os.system('adb shell input swipe 19 99 10 2 ' + str(int(res * 1.37)))
    a = cv2.resize(a, (540, 960))
    cv2.imshow('A', a)
    cv2.waitKey(0)
