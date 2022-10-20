from django.shortcuts import render
import cv2
import numpy as np
# Create your views here.
import os
import time
from django.core.mail import EmailMessage,BadHeaderError, send_mail
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from myemail import my_send_mail
class VideoCamera(object):
    width = 1280
    height = 960
    #靈敏度
    fast=2000
    # 計算畫面面積
    area = width * height
    # 輸出目錄
    outputFolder = "my_output"
    timeo= 1
    timeF = 200 #陣數間格
    #計算目前秒數
    min = 0
    def __init__(self):
         # 自動建立目錄
        if not os.path.exists(self.outputFolder):
         os.makedirs(self.outputFolder)
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(1,cv2.CAP_DSHOW)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
        # 設定擷取影像的尺寸大小
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH,self.width)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT,self.height)
    def __del__(self):
        self.video.release()
    def send_mail(self):
       # 電子郵件內容樣板
            localtime = time.localtime()
            result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime)
            nmin= time.strftime("%Y-%m-%d %I:%M", localtime)
            subject = "移動偵測信通知信"
            message="監視器在 " + result + "偵測到移動!! url:https://happy.shengda.ga/monitor/"
            from_email=settings.EMAIL_HOST_USER
            if(nmin!=self.min):
              my_send_mail(subject, message,from_email, ['computer30422@gmail.com'])
              self.min=nmin
  

def gen(camera):
   
    # 初始化平均影像
    ret, frame = camera.video.read()
    if(camera.video.isOpened()):
      avg= cv2.blur(frame, (4, 4))
      avg_float = np.float32(avg)

    while (camera.video.isOpened()):
        success, frame = camera.video.read()
         # 若讀取至影片結尾，則跳出
        if success == False:
            break
          # 模糊處理
        blur = cv2.blur(frame, (4, 4))

        # 計算目前影格與平均影像的差異值
        diff = cv2.absdiff(avg, blur)

        # 將圖片轉為灰階
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # 篩選出變動程度大於門檻值的區域
        ret, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)

        # 使用型態轉換函數去除雜訊
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 產生等高線
        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hasMotion = False
        for c in cnts:
            # 忽略太小的區域
            if cv2.contourArea(c) < camera.fast:
             continue

            # 偵測到物體，可以自己加上處理的程式碼在這裡...
            hasMotion = True
            # 計算等高線的外框範圍
            (x, y, w, h) = cv2.boundingRect(c)

            # 畫出外框
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if hasMotion:
         # 儲存有變動的影像
            if(camera.timeo % camera.timeF == 0):
              localtime = time.localtime()
              result = time.strftime("%Y%m%d%I%M%S%p", localtime)
              cv2.imwrite("%s/output_%s.jpg" % (camera.outputFolder, result), frame)
              camera.send_mail()
        camera.timeo += 1
        # 畫出等高線（除錯用）
        #cv2.drawContours(frame, cnts, -1, (0, 255, 255), 2)

        # 顯示偵測結果影像
        #cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 更新平均影像
        cv2.accumulateWeighted(blur, avg_float, 0.01)
        avg = cv2.convertScaleAbs(avg_float)
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
def gen1(camera):
   
    # 初始化平均影像
    ret, frame = camera.video.read()
    if(camera.video.isOpened()):
      avg= cv2.blur(frame, (4, 4))
      avg_float = np.float32(avg)

    while (camera.video.isOpened()):
        success, frame = camera.video.read()
         # 若讀取至影片結尾，則跳出
        if success == False:
            break
          # 模糊處理
        blur = cv2.blur(frame, (4, 4))

        # 計算目前影格與平均影像的差異值
        diff = cv2.absdiff(avg, blur)

        # 將圖片轉為灰階
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # 篩選出變動程度大於門檻值的區域
        ret, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)

        # 使用型態轉換函數去除雜訊
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 產生等高線
        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hasMotion = False
        for c in cnts:
            # 忽略太小的區域
            if cv2.contourArea(c) < 500:
             continue

            # 偵測到物體，可以自己加上處理的程式碼在這裡...
            hasMotion = True
            # 計算等高線的外框範圍
            (x, y, w, h) = cv2.boundingRect(c)

            # 畫出外框
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # 畫出等高線（除錯用）
        #cv2.drawContours(frame, cnts, -1, (0, 255, 255), 2)

        # 顯示偵測結果影像
        #cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 更新平均影像
        cv2.accumulateWeighted(blur, avg_float, 0.01)
        avg = cv2.convertScaleAbs(avg_float)
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
               