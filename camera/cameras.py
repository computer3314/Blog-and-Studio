import queue
import threading

import cv2
import numpy as np
# Create your views here.
import os
import time
from django.conf import settings
from myemail import my_send_mail

import datetime
from camera.models import Camera
class CameraException(Exception):
    message = None

    # 初始化異常
    def __init__(self, message: str):
        # 初始化異常描述
        self.message = message

    def __str__(self):
        return self.message


class BaseCamera:
    #相機對象
    cam = None
    # 保存每一幀讀取的畫面
    queue_image = queue.Queue(maxsize=10)
    # 後台取幀數的線程
    thread = None
    # 相機modal
    camera_model = None
    width = 500
    height = 500
     # 輸出目錄
    outputFolder = "my_output"
    # 移動畫面
    check_frame = None
    
    #計算目前秒數
    min = '2022-01-01 8:01:01'
     #靈敏度
    fast=2000
    # 相機基礎類
    Dday = 1
    def __init__(self, camera_model: Camera):
        
        self.cam = cv2.VideoCapture(camera_model.camera_api())
         # 自動建立目錄
        if not os.path.exists(self.outputFolder):
         os.makedirs(self.outputFolder)
        else:
         self._removeold()
        if self.cam.isOpened():
            # 相機打開成功
            self.thread = threading.Thread(target=self._thread, daemon=True)
            self.thread.start()
        else:
            # 打開是失敗
            raise CameraException("訪問失敗")
   
    def _thread(self):
        """
      opencv讀取時會將信息存儲到緩存區裡，處理速度小於緩存區速度，會導致資源積累
        """
        # 線程一直讀取影片流，將最新的視頻流存在隊列中
        while self.cam.isOpened():
            ret, img = self.cam.read()
            if not ret or img is None:
                # 讀取失敗
                pass
            else:
                # 讀取內容成功，將數據存放在緩存區
                if self.queue_image.full():
                    # 對列滿了，出對
                    self.queue_image.get()
                    # 插入最後面
                    self.queue_image.put(img)
                else:
                    # 插入最後面
                    self.queue_image.put(img)

    # 直接讀取圖片
    def read(self):
        """
       直接讀取從rtsp流中獲取到的圖片，不進行額外加工
        可能為空，需做判空處理
        """
        return self.queue_image.get()
    def send_mail(self):
       # 電子郵件內容樣板
            localtime = time.localtime()
            check=self.timeSecond()
            if check is not None:           
                result = time.strftime("%Y-%m-%d %I:%M:%S", localtime)
                result1 = time.strftime("%Y%m%d%I%M%S%p", localtime)
                subject = "移動偵測信通知信"
                message="監視器在 " + check + "偵測到移動!! url:https://happy.shengda.ga/monitor/"
                from_email=settings.EMAIL_HOST_USER
                my_send_mail(subject, message,from_email, ['computer30422@gmail.com'])
                cv2.imwrite("%s/output_%s.jpg" % (self.outputFolder, result1), self.check_frame)
    #時間相減
    def timeSecond(self):
        now_time=datetime.datetime.now()
        now_time=now_time.strftime("%Y-%m-%d %I:%M:%S")
        now_timer = datetime.datetime.strptime(now_time, r"%Y-%m-%d %I:%M:%S")
        end_time= self.min
        end_time = datetime.datetime.strptime(end_time, r"%Y-%m-%d %I:%M:%S")
        diff = now_timer - end_time
        if(diff.total_seconds() > 30):
            self.min = now_time
            return now_time
        else:
            return None
    #判斷過期檔案
    def shouldkeep(self,file):
     if datetime.datetime.fromtimestamp( os.path.getmtime(file) ) > \
        datetime.datetime.now() - datetime.timedelta(self.Dday):
        return True
    def _removeold(self):
        for i in os.walk(self.outputFolder):
            for j in i[2]:
                if not self.shouldkeep(os.path.join(i[0],j)):
                 os.remove( os.path.join(i[0],j) )
    def get_frame(self,admin):
        """
        獲取加工後的圖片，可以直接返回給前端顯示
        """
        img = self.queue_image.get()
        if img is None:
            return None
        else:       
            ret, frame = self.cam.read()
            if(self.cam.isOpened()):
                avg= cv2.blur(frame, (4, 4))
                avg_float = np.float32(avg) 
            blur = cv2.blur(img, (4, 4))

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
                if cv2.contourArea(c) < self.fast:
                 continue
                # 偵測到物體，可以自己加上處理的程式碼在這裡...
                hasMotion = True
                # 計算等高線的外框範圍
                (x, y, w, h) = cv2.boundingRect(c)

                # 畫出外框
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if hasMotion:
                self.check_frame=img
                if admin is not None:
                 self.send_mail()
         # 儲存有變動的影像
            # 畫出等高線（除錯用）
            #cv2.drawContours(frame, cnts, -1, (0, 255, 255), 2)

            # 顯示偵測結果影像
            #cv2.imshow('frame', frame)
            # 更新平均影像
            cv2.accumulateWeighted(blur, avg_float, 0.01)
            avg = cv2.convertScaleAbs(avg_float)
            #壓縮圖片，否則圖片過大，編碼效率慢，視頻延遲過高
            img = cv2.resize(img, (self.width, self.height), fx=0.25, fy=0.25)
            # 對圖片進行編碼
            ret, jpeg = cv2.imencode('.jpeg', img)
            self.oldImg = img
            return jpeg.tobytes()


class CameraFactory:
    """
    相機工廠
    """
    # 存儲實例化的所有相機
    cameras = {}

    @classmethod
    def get_camera(cls, camera_id: int):
        # 通過ID取得相機
        camera = cls.cameras.get(camera_id)
        if camera is None:
            # 查看像是否存在
            try:
                camera_model = Camera.objects.get(id=camera_id)
                base_camera = BaseCamera(camera_model=camera_model)
                if base_camera is not None:
                    cls.cameras.setdefault(camera_id, base_camera)
                    return cls.cameras.get(camera_id)
                else:
                    return None
            except Camera.DoesNotExist:
                # 相機不存在
                return None
            except CameraException:
                # 相機實例失敗
                return None
        else:
            # 存在相機，直接返回
            return camera
