import queue
import threading

import cv2
import numpy as np
# Create your views here.
import os
import time
from django.conf import settings
from myemail import my_send_mail
from PIL import Image,ImageSequence
import datetime
from camera.models import Camera,Move,File
from dbcheck import db_retry
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
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
    #相機Modal
    camera_model=None
    # 後台取幀數的線程
    thread = None
    queue = None
    #相機名稱
    title =None
    Camera_id=None
    #錄影機
    output=None
    file_model=None
    #偵測錄影第一張照片寫入
    fileinsert=0
    #解析度設定
    width = 1280
    height = 720
    #實際上相機尺寸
    trueHeight=1280
    trueWidth=720
    today=None
     # 輸出目錄
    outputBaseFolder = "static/my_output/"
    #圖片截圖目錄
    outputFolder = None
    #影片截圖目錄
    outputVideoFolder=None
    #目前使用video
    nowoutVideo=None
    videostart=None
    #計算幀數
    counter = 0
    #錄影圖樣顯示頻率
    recordcount=0
    recordLimit=10
    fps = 10
    start_time=time.time()
    #計算目前秒數
    min = '2022-01-01 8:01:01'
     #靈敏度
    fast=4

    #移動偵測通知時間(秒數)
    moveNotice = 60
    #是否開啟寄信
    mail_check=False
    #是否移動拍照
    scan_check=True
     #是否連續錄製
    video_check=True
    #是否啟動
    isOpened=True
    #畫面平均值
    avg=0
    avg_float=0
    #直播中字體位置
    #時間
    org = (0,0)
    #fps
    org1 = (0,0)   
    #錄影中
    org2 = (0,0) 
    recording=False
    # 相機基礎類
    def __init__(self, camera_model: Camera):
        self.set_defalut(camera_model)
        self.cam = cv2.VideoCapture(camera_model.camera_api(),cv2.CAP_DSHOW)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        
        self.set_defalut1()
        if self.cam is None:
             # 打開失敗
            logger.error("編號:" + self.Camera_id + " 找不到此相機")
            raise CameraException("編號:" + self.Camera_id + " 找不到此相機")
        # 自動建立影像截圖目錄
        self.outputFolder=self.outputBaseFolder+str(self.title)       
        if not os.path.exists(self.outputFolder):
         os.makedirs(self.outputFolder)
         # 自動建立影片目錄
        self.outputVideoFolder=self.outputBaseFolder+str(self.title) +"video"     
        if not os.path.exists(self.outputVideoFolder):
         os.makedirs(self.outputVideoFolder)
        if self.cam is None:
              # 打開失敗
            logger.error("編號:" + self.Camera_id + " 找不到此相機")
            raise CameraException("編號:" + self.Camera_id + " 找不到此相機")
        elif self.isOpened is False:
             logger.warn(msg)("編號:" + self.Camera_id + " 相機已經關閉")
             raise CameraException("編號:" + self.Camera_id + " 相機已經關閉")
        elif self.cam.isOpened():
            # 相機打開成功
              # 影片寫入
            self.get_output_video(False)
            self.thread = threading.Thread(target=self._thread,args=())
            self.thread.daemon = True
            self.thread.start()
            
        else:
            # 打開失敗
            logger.error("編號:" + self.Camera_id +" 相機訪問失敗")
            raise CameraException("編號:" + self.Camera_id +"相機訪問失敗")
    def  __del__(self):
        if self.cam is not None:
            self.cam.release()
            logger.info("編號:" + self.Camera_id +" 釋放相機")
        if self.output is not None:
            self.output.release()
    def get_output_video(self,isStop:bool):
        if self.cam is not None and self.video_check:
              if isStop is False:
                self.nowoutVideo=self.getAviNameWithDate()
              # 使用 XVID 編碼(‘M’, ‘P’, ‘4’, ‘2’)(‘M’, ‘P’, ‘4’, ‘2’)
              fourcc = cv2.VideoWriter_fourcc(*'avc1')
              #fourcc = 0x31637661
              #fourcc =cv2.VideoWriter_fourcc(*'XVID')
              self.output= cv2.VideoWriter('%s' % (self.nowoutVideo), fourcc,6,(self.trueWidth,self.trueHeight))
              self.camera_model.file.create(movie= self.nowoutVideo)
              self.file_model=File.objects.select_for_update().filter(movie=self.nowoutVideo)
              self.fileinsert=0
    def close_file(self):
        #更換影片檔時呼叫
        if self.output is not None:
            if self.file_model is not None: #沒圖片後 若有file就增加結束時間
                    self.file_model.update(endtime=datetime.datetime.now())
                    self.output.release()
                    self.output=None
                    # if self.file_model[0].starttime is None:
                    #       os.remove(self.file_model[0].movie)#沒有時長  刪除檔案
                    #       self.file_model.delete()
                    #       logger.info("編號:" + self.Camera_id +" 刪除沒有時長的影片")
                    self.file_model=None #清空file物件  等等會建立新的
                       


    def getAviNameWithDate(self,nameIn="output.mp4"):
        #計算當日影片是否重複
        """Needs a file ending on .avi, inserts _<date> before .avi. 

        If file exists, it appends a additional _number after the <date> 
        ensuring filename uniqueness at this time."""
        if not nameIn.endswith(".mp4"):
            raise ValueError("filename must end on .mp4")

        filename = self.outputVideoFolder+"/"+nameIn.replace(".mp4","_{0}.mp4").format(datetime.datetime.now().strftime("%Y-%m-%d"))
        if os.path.isfile(filename):             # if already exists
            fn2 = filename[0:-4]+'_{0}.mp4'          # modify pattern to include a number
            count = 1
            while True: # increase number until file not exists
                if db_retry(File.objects.filter(movie = fn2.format(count)).count()) == 0:
                    if(os.path.isfile(fn2.format(count)) is False):
                      break
                count += 1
            logger.info("寫入檔案:"+fn2.format(count))     
            return fn2.format(count)                 # return file with number in it

        else:          
            logger.info("寫入檔案:"+filename)                          # filename ok, return it
            return filename

    def set_defalut(self,camera_model: Camera):
        #讀取基礎設定
        self.camera_model=camera_model
        self.today=time.strftime("%Y-%m-%d",time.localtime(time.time()))
        self.width=camera_model.width
        self.height=camera_model.heigth
        self.fast=camera_model.fast
        self.moveNotice=camera_model.moveNotice
        self.mail_check=camera_model.mailCheck
        self.scan_check=camera_model.scancheck
        self.fps=camera_model.fps
        self.isOpened=camera_model.isOpened
        self.title=camera_model.title
        self.Camera_id=camera_model.camera_id
        self.video_check=camera_model.videocheck
        logger.info("編號:" + self.Camera_id + " 相機基礎設定")
    def set_defalut1(self):
        if self.cam is not None:
            logger.info("編號:" + self.Camera_id + " 相機長寬fps設定")
            self.cam.set(cv2.CAP_PROP_FPS,int(self.fps))
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.trueHeight=int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.trueWidth=int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.org = (10,int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)/24))
            self.org1 = (int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)*0.8),int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)/24))
            self.org2 = (int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)*0.9),int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)/24))
            if self.isOpened is False:
                self.cam=None
    def _thread(self):
        """
      opencv讀取時會將信息存儲到緩存區裡，處理速度小於緩存區速度，會導致資源積累
        """
        # 線程一直讀取影片流，將最新的視頻流存在隊列中

        if self.cam is not None:
                self.queue =queue.Queue(maxsize=10)
                while True:
              
                    if self.cam is None:
                        logger.error("編號:" + self.Camera_id + " 相機讀取相機失敗")
                        break
                    if self.isOpened is False:
                        logger.warn("編號:" + self.Camera_id + " 相機已經關閉")
                        break
                    ret, img = self.cam.read()
                    if not ret or img is None:
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
                
    def move_notice(self,img):
       # 移動偵測
            check=self.timeSecond(self.moveNotice)#確認是否達到偵測時間
            if check is not None:
                localtime = time.localtime()
                result1 = time.strftime("%Y%m%d%I%M%S%p", localtime)
                if self.mail_check:     #是否寄信
                    url=settings.PRO_HOST + self.outputFolder + "/output_" + result1 + ".jpg"     
                    self.send_mail(check,url)
                if self.scan_check: #確認是否截圖
                    self.photo_scan(img,result1)
                nowvideo=""
                if self.video_check:#確認是否錄影
                    nowvideo=self.nowoutVideo
                     #新增一筆紀錄到資料庫
                db_retry(self.insertvalue(result1,nowvideo))
                logger.info("編號:" + self.Camera_id + " 相機在"+result1+"偵測到移動傳入資料庫")
    def insertvalue(self,result1,nowvideo):
        move=self.camera_model.move.create(photo="%s/output_%s.jpg" % (self.outputFolder, result1),movie=nowvideo)
        return move
    def send_mail(self,checkTime,url):
        #寄信
        try:             
           subject = "移動偵測信通知信"
           message="監視器:" + str(self.title) + "在 " + checkTime + "偵測到移動!! url:"+url
           from_email=settings.EMAIL_HOST_USER
           my_send_mail(subject, message,from_email, ['computer30422@gmail.com'])
           logger.info("編號:" + self.Camera_id + "相機成功發送信件"+checkTime)
        except:                 
            logger.error("編號:" + self.Camera_id +' 相機發送信件失敗'+checkTime)
    def photo_scan(self,img,result1):
        #拍照
        try:                
           cv2.imwrite("%s/output_%s.jpg" % (self.outputFolder, result1), img)
           logger.info("編號:" + self.Camera_id + "相機成功儲存檔案"+result1)
        except:                 
            logger.error("編號:" + self.Camera_id +' 相機儲存檔案失敗'+result1)
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
        recording="REC"
        cv2.putText(image, now_time, self.org, fontFace, fontScale, color, thickness, lineType)
        cv2.putText(image, text, self.org1, fontFace, fontScale, color, thickness, lineType)
        if self.recording:
            cv2.putText(image, recording, self.org2, fontFace, fontScale, color, thickness, lineType)
    def get_move(self,img):
        if self.cam is not None and self.cam.isOpened():
            try:
                ret, frame = self.cam.read()
                self.avg= cv2.blur(frame, (4, 4))
                blur = cv2.blur(img, (4, 4))
                    # 計算目前影格與平均影像的差異值
            
                diff = cv2.absdiff(self.avg, blur)
            except:
                return None
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
    def writer_video(self,img):
        if self.output is not None and self.video_check:
            if self.fileinsert == 0:
                if self.file_model is not None: #若有檔案sql 就增加結束時間
                    self.file_model.update(starttime=datetime.datetime.now())
                    self.fileinsert+=1
            if self.recordcount == self.recordLimit:
                self.recording=True
                self.recordcount=0
            else:
                self.recordcount+=1
            self.output.write(img)#寫入影片
    def get_frame(self,role):
        """
        取得畫面給前端看
        """
        img = self.queue.get()
        # ret, img = self.cam.read()
        if img is None:
            return None
        else:                
            self.makefps(img)
            self.recording=False
            if role == "admin":
                self.get_move(img)
                self.writer_video(img)
            #壓縮圖片，否則圖片過大，編碼效率慢，視頻延遲過高
            shape = img.shape
            shape = (int(shape[1]), int(shape[0]))
            img = cv2.resize(img, shape, interpolation=cv2.INTER_CUBIC)
            #img = cv2.resize(img, (self.width, self.height), fx=0.25, fy=0.25)
            # 對圖片進行編碼
            ret, jpeg = cv2.imencode('.jpeg', img)
            
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
            logger.info("相機不存在")
            return None
        else:      
            # 存在相機，直接返回
            logger.info("編號:" + camera_id + " 相機取得成功")
            return camera
    @classmethod 
    def check_camera(cls, camera_id: int):
         # 通過ID取得相機    #檢查相機是否存在
        camera = cls.cameras.get(camera_id)
        if camera is None:
            return None
        else:
             return camera
    @classmethod
    def update_camera(cls, camera: Camera):
            
                camera_id=camera.camera_id
                oldcamera = cls.cameras.get(camera_id)
                if oldcamera is None:
                    logger.info("新增編號:" + camera_id + " 相機開始")
                    try:
                        base_camera = BaseCamera(camera_model=camera)
                        if base_camera is not None:
                                cls.cameras.setdefault(camera_id, base_camera)
                                logger.info("編號:" + camera_id + " 相機建立成功")
                        else:
                                logger.error("編號:" + camera_id + " 相機建立失敗")
                    except Camera.DoesNotExist:
                        # 相機不存在
                      logger.warn=("資料庫不存在此相機 編號:"+camera_id)
                    except CameraException:
                    # 相機實例失敗
                        logger.warn("編號:" + camera_id + " 相機實例化失敗")  
                    logger.info("新增編號:" + camera_id + " 相機結束") 
                else:
                    logger.info("更新編號:" + camera_id + " 相機開始")
                    # if oldcamera.cam is None:
                    try:
                            oldcamera.close_file()#停止錄影
                            base_camera = BaseCamera(camera_model=camera)
                            if base_camera is not None:
                                    cls.cameras.update({camera_id: base_camera})
                                    logger.info("編號:" + camera_id + " 相機建立成功")
                            else:
                                    logger.error("編號:" + camera_id + " 相機建立失敗")
                    except Camera.DoesNotExist:
                        # 相機不存在
                          logger.warn("資料庫不存在此相機 編號:"+camera_id)
                    except CameraException:
                         # 相機實例失敗
                           logger.error("編號:" + camera_id + " 相機實例化失敗")  
                    # else:
                    #     oldcamera.close_file()#停止錄影
                    #     oldcamera.set_defalut(camera) #基本配置更新
                    #     oldcamera.set_defalut1() #基本配置更新           
                    #     oldcamera.get_output_video(False) #更新錄影檔案
                    logger.info("更新編號:" + camera_id + " 相機結束")
                    
        
    @classmethod
    def update_ALLcamera(cls):
           cameras = Camera.objects.all()
           logger.info("啟動所有相機實例開始")
           for camera in cameras:
             cls.update_camera(camera)
           logger.info("啟動所有相機實例結束")
    @classmethod
    def loadingpic(cls):
        loadingPic="static/assets/img/close.png"
        im = cv2.imread(loadingPic, cv2.IMREAD_UNCHANGED)
        return im
    @classmethod
    def get_cameratoVideo(cls, camera_id: int,isStop:bool):
        # 通過ID取得相機
        camera = cls.cameras.get(camera_id)
        if camera is not None:
            if isStop:
                camera.close_file()#關閉目前錄影
            else:
                camera.get_output_video(False)#重新抓取錄影video
        
    @classmethod
    def get_cameranowVideo(cls, camera_id: int):
        # 取得相機目前video
        camera = cls.cameras.get(camera_id)
        if camera is not None and camera.output is not None:
                return camera.nowoutVideo #回傳目前使用的video
        else:
            return None
    @classmethod
    def returnCameraIndexes(cls):
    # 取得相機index
        index = 0
        arr = []
        while True:
            cap = cv2.VideoCapture(index)
            try:
                if cap.getBackendName()=="MSMF":
                    arr.append(index)
            except:
                break
            cap.release()
            index += 1
        return arr

