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
from .models import Move
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
    #相機名稱
    title =None
    Camera_id=None
    #解析度設定
    width = 1280
    height = 720
     # 輸出目錄
    outputBaseFolder = "static/my_output/"
    outputFolder = None
    #計算幀數
    counter = 0
    fps = 10
    fpsms=0
    start_time=time.time()
    #計算目前秒數
    min = '2022-01-01 8:01:01'
     #靈敏度
    fast=4
   #檔案超過多久刪除(天數)
    Dday = 1
    #移動偵測通知時間(秒數)
    moveNotice = 60
    #是否開啟寄信
    mail_check=False
    #是否移動拍照
    scan_check=True
    #是否啟動
    isOpened=True
    isstop = False
    avg=0
    avg_float=0

    # 相機基礎類
    def __init__(self, camera_model: Camera,queue_image:queue):
        
        self.cam = cv2.VideoCapture(camera_model.camera_api(),cv2.CAP_DSHOW)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        self.cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*"MJPG"))
        if self.cam is None:
             # 打開失敗
            print("找不到此相機")
            raise CameraException("找不到此相機")
        else:
            self.set_defalut(camera_model)
        self.outputFolder=self.outputBaseFolder+str(self.title)       
        # 自動建立目錄
        if not os.path.exists(self.outputFolder):
         os.makedirs(self.outputFolder)
        else:
         self._removeold()
        if self.cam is None:
              # 打開失敗
            print("找不到此相機")
            raise CameraException("找不到此相機")
        elif self.isstop is True:
             print("已經暫停")
             raise CameraException("已經暫停")
        elif self.isOpened is False:
             print("已經關閉")
             raise CameraException("已經關閉")
        elif self.cam.isOpened():
            self.queue=queue_image
            # 相機打開成功
            self.thread = threading.Thread(target=self._thread, daemon=True, args=())
            self.thread.start()
        else:
            # 打開失敗
            print("訪問失敗")
            raise CameraException("訪問失敗")
    def __del__(self):
        self.cam.release()
    def stop(self):
	# 記得要設計停止無限迴圈的開關。
        self.isstop = True
        print('相機暫停!')
    def set_defalut(self,camera_model: Camera):
        #讀取基礎設定
        self.width=camera_model.width
        self.height=camera_model.heigth
        self.fast=camera_model.fast
        self.Dday=camera_model.dday
        self.moveNotice=camera_model.moveNotice
        self.mail_check=camera_model.mailCheck
        self.scan_check=camera_model.scancheck
        self.fps=camera_model.fps
        self.isOpened=camera_model.isOpened
        self.title=camera_model.title
        self.Camera_id=camera_model.camera_id
        self.fpsms=1/self.fps
        self.cam.set(cv2.CAP_PROP_FPS,self.fps)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if self.isOpened is False:
            self.cam=None
        
    def _thread(self):
        """
      opencv讀取時會將信息存儲到緩存區裡，處理速度小於緩存區速度，會導致資源積累
        """
        # 線程一直讀取影片流，將最新的視頻流存在隊列中
        if self.cam is not None:
            while self.cam.isOpened() and (not self.isstop):
                ret, img = self.cam.read()
                #time.sleep(self.fpsms)
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
            print("結束佇列")
            self.__del__()
    def move_notice(self,img):
       # 移動偵測
            check=self.timeSecond(self.moveNotice)
            if check is not None:
                localtime = time.localtime()
                result1 = time.strftime("%Y%m%d%I%M%S%p", localtime)

                if self.mail_check:      
                    url=settings.PRO_HOST + self.outputFolder + "/output_" + result1 + ".jpg"     
                    self.send_mail(check,url)
                if self.scan_check: 
                    self.photo_scan(img,result1)
                else:
                    url=None
                #新增一筆紀錄到資料庫
                Move.objects.create(camera_id=self.Camera_id,photo="%s/output_%s.jpg" % (self.outputFolder, result1))
            
           
    def send_mail(self,checkTime,url):
        #寄信
        try:             
           subject = "移動偵測信通知信"
           message="監視器:" + str(self.title) + "在 " + checkTime + "偵測到移動!! url:"+url
           from_email=settings.EMAIL_HOST_USER
           my_send_mail(subject, message,from_email, ['computer30422@gmail.com'])
           print("成功發送信件")
        except:                 
            print('發送信件失敗')
    def photo_scan(self,img,result1):
        #拍照
        try:                
           cv2.imwrite("%s/output_%s.jpg" % (self.outputFolder, result1), img)
           print("成功儲存檔案")
        except:                 
            print('儲存檔案失敗')
    #時間相減
    def timeSecond(self,Second):
        now_time=datetime.datetime.now()
        now_time=now_time.strftime("%Y-%m-%d %H:%M:%S")
        now_timer = datetime.datetime.strptime(now_time, r"%Y-%m-%d %H:%M:%S")
        end_time= self.min
        end_time = datetime.datetime.strptime(end_time, r"%Y-%m-%d %H:%M:%S")
        diff = now_timer - end_time
        if(diff.total_seconds() > Second):
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
        org = (10,30)
        org1 = (1080,30)
        fontFace = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
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
        now_time=now_time.strftime("%Y-%m-%d %H:%M:%S")
        text = "FPS :"+str(self.fps)
        cv2.putText(image, now_time, org, fontFace, fontScale, color, thickness, lineType)
        cv2.putText(image, text, org1, fontFace, fontScale, color, thickness, lineType)
    def get_move(self,img):
        if self.cam is not None and self.cam.isOpened():
            ret, frame = self.cam.read()
            self.avg= cv2.blur(frame, (4, 4))
            blur = cv2.blur(img, (4, 4))
                # 計算目前影格與平均影像的差異值
            diff = cv2.absdiff(self.avg, blur)
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
                    #(x, y, w, h) = cv2.boundingRect(c)

                    # 畫出外框
                    #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)         
            if hasMotion:
                self.move_notice(frame)
         # 儲存有變動的影像
            # 畫出等高線（除錯用）
            #cv2.drawContours(frame, cnts, -1, (0, 255, 255), 2)        
            # 更新平均影像
            #cv2.accumulateWeighted(blur, avg_float, 0.01)
            self.avg = cv2.convertScaleAbs(self.avg_float)
            self.avg_float = np.float32(self.avg) 
        # 直接讀取圖片
    def get_frame(self,role):
        """
        取得畫面給前端看
        """
        
        img = self.queue.get()
        if img is None:
            return None
        else:
                    
            self.makefps(img)
            if role == "admin":
                self.get_move(img)
            #壓縮圖片，否則圖片過大，編碼效率慢，視頻延遲過高
            img = cv2.resize(img, (self.width, self.height), fx=0.25, fy=0.25)
            # 對圖片進行編碼
            ret, jpeg = cv2.imencode('.jpeg', img)
            #cv2.waitKey(self.fps)
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
        camera_model = Camera.objects.get(camera_id=camera_id)
        if camera is None:
            print("不存在cameras")
            # 查看像是否存在
            try:
                base_camera = BaseCamera(camera_model=camera_model,queue_image=queue_image)
                if base_camera is not None:
                    cls.cameras.setdefault(camera_id, base_camera)
                    print("建立成功")
                    return cls.cameras.get(camera_id)
                else:
                    print("不存在")
                    return None
            except Camera.DoesNotExist:
                # 相機不存在
                print("資料庫不存在此相機")
                return None
            except CameraException:
                # 相機實例失敗
                print("相機實例化失敗")
                return None
        else:
            # 存在相機，直接返回
            print("已存在")
            #camera.set_defalut(camera_model)
            return camera
       
