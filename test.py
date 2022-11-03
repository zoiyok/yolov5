import numpy as np
import cv2 as cv
import time


class Car:
    def __init__(self, c_id, c_x, c_y, direction, c_count, c_start_time, c_over_time, c_v):
        self.c_id = c_id
        self.c_x = c_x
        self.c_y = c_y
        self.direction = direction
        self.c_count = c_count
        self.c_start_time = c_start_time
        self.c_over_time = c_over_time
        self.c_v = c_v

    def updateCoords(self, x, y):
        self.c_x = x
        self.c_y = y


count_up = 0
count_down = 0
cars = []
pid = 1
max_v = 0
distance = 10
vc = cv.VideoCapture(r"video/test.mp4")

fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('output.avi', fourcc, 15, (1920, 1080))

BS = cv.createBackgroundSubtractorMOG2(detectShadows = True)
while (vc.isOpened()):
    ret, frame = vc.read()
    # cv.imshow("frame01",frame)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # ret,gray = cv.threshold(gray,127,255,cv.THRESH_BINARY)
    fgmask = BS.apply(gray)
    image = cv.medianBlur(fgmask, 5)
    # cv.imshow("BS",fgmask)
    element = cv.getStructuringElement(cv.MORPH_RECT, (5, 5));  # 创建结构体
    image2 = cv.morphologyEx(image, cv.MORPH_CLOSE, element, iterations = 5);  # 闭运算
    # image3 = cv.erode(image2, element)
    image3 = cv.morphologyEx(image2, cv.MORPH_OPEN, element, iterations = 5)
    # cv.imshow('frame1', image3)
    contours, hierarchy = cv.findContours(image3, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    cv.line(frame, (0, 700), (1920, 700), (0, 255, 0), 3)
    cv.line(frame, (0, 400), (1920, 400), (0, 255, 0), 3)
    cv.line(frame, (0, 800), (1920, 800), (255, 255, 255), 2)
    cv.line(frame, (0, 300), (1920, 300), (255, 255, 255), 2)
    cv.putText(frame, "Up:" + str(count_up), (1100, 100), cv.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)
    cv.putText(frame, "Down:" + str(count_down), (700, 100), cv.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)
    cv.putText(frame, "max_v:" + str('%.2f' % (max_v * 3.6)) + 'km/h', (50, 100), cv.FONT_HERSHEY_COMPLEX, 1.5,
               (255, 0, 0), 2)
    null = True  # 如果这一帧没有检测到任何车，则将cars置空，减小误差,设置初始变量null设为True
    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        cx = int(x + w / 2)
        cy = int(y + h / 2)
        if 300 < int(y + (h / 2)) < 800 and 400 < int(x + (w / 2)) < 1800:
            if cv.contourArea(cnt) < 13000 or w < 100 or h < 100:
                continue
            null = False  # 有车时不会清空
            new = True  # 是否创建车辆
            for i in cars:
                if abs(cx - i.c_x) < 100 and abs(cy - i.c_y) < 100:  # 找到这辆车与上一帧中最近的车
                    # cv.putText(frame, 'cid:' + str(i.c_id), (x, y-10), cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
                    # cv.putText(frame, "now_v:" + str('%.4f' % (i.c_v)) + 'm/s', (x, y-10),
                    #            cv.FONT_HERSHEY_COMPLEX, 1,
                    #            (255, 0, 0), 2)
                    new = False
                    i.updateCoords(cx, cy)  # 更新车辆位置信息
                    if 700 <= i.c_y <= 720 and i.direction == 'down' and i.c_count == False:
                        i.c_over_time = time.time()
                        i.c_v = distance / (i.c_over_time - i.c_start_time)
                        if i.c_v > max_v:
                            max_v = i.c_v
                        count_down += 1
                        i.c_count = True
                    if 380 <= i.c_y <= 400 and i.direction == 'up' and (i.c_count == False):
                        i.c_over_time = time.time()
                        i.c_v = distance / (i.c_over_time - i.c_start_time)
                        if i.c_v > max_v:
                            max_v = i.c_v
                        count_up += 1
                        i.c_count = True
                if i.c_y > 720 or i.c_y < 380:
                    cars.remove(i)  # 超过一定范围，删除对象

            if new == True and 340 < cy < 760:  # 符合一定条件，创建对象
                start_time = time.time()
                p = Car(pid, cx, cy, 'unknow', False, start_time, 0, 0)
                if p.c_x < 1000:
                    p.direction = 'down'
                else:
                    p.direction = 'up'
                cars.append(p)
                pid += 1
            cv.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
    if null == True:  # 该帧没车，清空cars
        cars = []
    # cv.putText(frame, 'cars:' + str(len(cars)), (100, 100), cv.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)
    cv.imshow("frame", frame)
    out.write(frame)
    # cv.imshow('frame2', image3)
    # print(max_v*3.6)
    k = cv.waitKey(30) & 0xff
    if k == 27:
        break
vc.release()
cv.destroyAllWindows()
