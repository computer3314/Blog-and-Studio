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
    # 後台取幀數的線程
    thread = None
    queue = None
    # 相機modal
    camera_model = None
    width = 1920
    height = 1080
     # 輸出目錄
    outputFolder = "static/my_output"
    #計算幀數幀
    counter = 0
    fps = 0
    start_time=time.time()
    #計算目前秒數
    min = '2022-01-01 8:01:01'
     #靈敏度
    fast=4
   #檔案超過多久刪除
    Dday = 1
    # 相機基礎類
    def __init__(self, camera_model: Camera,queue_image:queue):
        
        self.cam = cv2.VideoCapture(camera_model.camera_api(),cv2.CAP_DSHOW)
         # 自動建立目錄
        if not os.path.exists(self.outputFolder):
         os.makedirs(self.outputFolder)
        else:
         self._removeold()
        if self.cam.isOpened():
            self.fps=self.cam.get(cv2.CAP_PROP_FPS)
            self.queue=queue_image
            # 相機打開成功
            self.thread = threading.Thread(target=self._thread, daemon=True)
            self.thread.start()
        else:
            # 打開是失敗
            self.cam = None
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
                if self.queue.full():
                    # 對列滿了，出對
                    self.queue.get()
                    # 插入最後面
                    self.queue.put(img)
                else:
                    # 插入最後面
                    self.queue.put(img)
    def __del__(self):
        self.cam.release()
    # 直接讀取圖片
    def read(self):
        """
       直接讀取從rtsp流中獲取到的圖片，不進行額外加工
        可能為空，需做判空處理
        """
        return self.queue_image.get()
    def send_mail(self,img):
       # 電子郵件內容樣板
            localtime = time.localtime()
            check=self.timeSecond()
            if check is not None:           
                result1 = time.strftime("%Y%m%d%I%M%S%p", localtime)
                subject = "移動偵測信通知信"
                message="監視器在 " + check + "偵測到移動!! url:https://happy.shengda.ga/camera"
                from_email=settings.EMAIL_HOST_USER
                my_send_mail(subject, message,from_email, ['computer30422@gmail.com'])
                cv2.imwrite("%s/output_%s.jpg" % (self.outputFolder, result1), img)
    #時間相減
    def timeSecond(self):
        now_time=datetime.datetime.now()
        now_time=now_time.strftime("%Y-%m-%d %I:%M:%S")
        now_timer = datetime.datetime.strptime(now_time, r"%Y-%m-%d %I:%M:%S")
        end_time= self.min
        end_time = datetime.datetime.strptime(end_time, r"%Y-%m-%d %I:%M:%S")
        diff = now_timer - end_time
        if(diff.total_seconds() > 60):
            self.min = now_time
            return now_time
        else:
            return None
    #判斷過期檔案
    def shouldkeep(self,file):
     if datetime.datetime.fromtimestamp( os.path.getmtime(file) ) > \
        datetime.datetime.now() - datetime.timedelta(self.Dday):
        return True
    #刪除檔案
    def _removeold(self):
        for i in os.walk(self.outputFolder):
            for j in i[2]:
                if not self.shouldkeep(os.path.join(i[0],j)):
                 os.remove( os.path.join(i[0],j) )
      #製作fps/time
    def makefps(self,image):
            # img 來源影像
            # text 文字內容
            # org 文字座標 ( 垂直方向是文字底部到影像頂端的距離 )
            # fontFace 文字字型
            # fontScale 文字尺寸
            # color 線條顏色，使用 BGR
            # thickness 文字外框線條粗細，預設 1
            # lineType 外框線條樣式，預設 cv2.LINE_8，設定 cv2.LINE_AA 可以反鋸齒   
        org = (10,10)
        org1 = (580,10)
        fontFace = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1/3
        color = (0,0,255)
        thickness = 1
        lineType = cv2.LINE_AA
        if(time.time() - self.start_time) > 1 : #目前顯示鎮數
            self.fps=self.counter
            self.counter=1
            self.start_time=time.time()
        else:
            self.counter +=1
        now_time=datetime.datetime.now()
        now_time=now_time.strftime("%Y-%m-%d %I:%M:%S %p")
        text = "FPS :"+str(self.fps)
        cv2.putText(image, now_time, org, fontFace, fontScale, color, thickness, lineType)
        cv2.putText(image, text, org1, fontFace, fontScale, color, thickness, lineType)
    def get_frame(self,admin):
        """
        獲取加工後的圖片，可以直接返回給前端顯示
        """
        img = self.queue.get()
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
            self.makefps(img)
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
                if admin is not None:
                 self.send_mail(img)
         # 儲存有變動的影像
            # 畫出等高線（除錯用）
            #cv2.drawContours(frame, cnts, -1, (0, 255, 255), 2)        

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
        queue_image = queue.Queue(maxsize=10)
        if camera is None:
            print("不存在cameras")
            # 查看像是否存在
            try:
                camera_model = Camera.objects.get(camera_id=camera_id)
                base_camera = BaseCamera(camera_model=camera_model,queue_image=queue_image)
                if base_camera is not None:
                    cls.cameras.setdefault(camera_id, base_camera)
                    return cls.cameras.get(camera_id)
                else:
                    print("不存在error")
                    return None
            except Camera.DoesNotExist:
                # 相機不存在
                print("不存在")
                return None
            except CameraException:
                # 相機實例失敗
                print("相機實例")
                return None
        else:
            # 存在相機，直接返回
            return camera
       
