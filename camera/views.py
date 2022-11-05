from django.http import HttpResponse,HttpResponseNotFound,StreamingHttpResponse,JsonResponse
import io
import re
import mimetypes
from django.shortcuts import render
from .cameras import CameraFactory, BaseCamera
from django.conf import settings
from PIL import Image,ImageSequence
import numpy as np
import cv2
import time
import zipfile
import datetime
from .models import Move,Camera,File
import os
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.core import serializers
import json
import shutil
from wsgiref.util import FileWrapper
import logging
from .filewapper import stream
# Get an instance of a logger
logger = logging.getLogger(__name__)
def turn_makeFrame(camera: BaseCamera,role,background:bool,camera_id,loading=None,makeFrame=None):
        while True:
            if camera is None  or camera.cam is None:
                logger.info("查無相機")
                loading=True
                makeFrame=False
                break
            frame = camera.get_frame(role)
            if frame is not None:
                if background is True:
                     #網頁背景執行，比較不會斷線
                    frame = str(time.time()).encode("utf-8")
                    if camera is None or camera.cam is None:
                        logger.info("相機已消失")
                        loading=True
                        makeFrame=False
                        break
                    yield (b'--frame\r\n'
                                b'Content-Type: text/plain;charset=utf-8\r\n\r\n' + frame + b'\r\n\r\n')  
                else:
                     #網頁前端執行，http有時候會斷開
                    if camera is None or camera.cam is None:
                        logger.info("相機已消失")
                        loading=True
                        makeFrame=False
                        break        
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')   
            else:
                logger.info("讀取不到影片")
                break
        frame = str(time.time()).encode("utf-8")
        yield (b'--frame\r\n'
                                b'Content-Type: text/plain;charset=utf-8\r\n\r\n' + frame + b'\r\n\r\n') 
def turn_loading(camera: BaseCamera,role,background:bool,camera_id,loading=None,makeFrame=None):
        Nimg=CameraFactory.loadingpic()
        logger.info("使用相機關閉中圖片")
        while True:
                truecamera = CameraFactory.check_camera(camera_id)
                if truecamera is not None and truecamera.cam is not None:
                    camera=truecamera
                    makeFrame=True
                    loading=False
                    break
                ret, jpeg = cv2.imencode('.jpeg', Nimg)
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        frame = str(time.time()).encode("utf-8")
        yield (b'--frame\r\n'
                                b'Content-Type: text/plain;charset=utf-8\r\n\r\n' + frame + b'\r\n\r\n')
def gen_display(camera: BaseCamera,role,background:bool,camera_id,loading=None,makeFrame=None):
    """
   直播影片生成器。
    """
    
    logger.info("開始顯示直播")
    truecamera: BaseCamera=None
    loading=loading
    makeFrame=makeFrame
    if loading is None and makeFrame is None:
        if camera is None or camera.cam is None:
            loading=True
            makeFrame=False
        else:
            makeFrame=True
            loading=False
    if loading is True:
       return turn_loading(camera,role,background,camera_id)
    if makeFrame is True:
       return turn_makeFrame(camera,role,background,camera_id)
def video(request):
    """
    影片流路由。將其放入img標記的src屬性中。
    例如：<img src='https://ip:port/uri' >
    """
    # 影片相機對象
    camera_id = request.GET.get('camera_id')
    role = request.GET.get('role')
    background = request.GET.get('background')
    if role is None:
        role="None"
    if background is None:
        background=False
    else:
        background=True
    camera: BaseCamera = CameraFactory.get_camera(camera_id)
    #使用流傳輸傳輸影片流
    reponse=StreamingHttpResponse(gen_display(camera,role,background,camera_id), content_type='multipart/x-mixed-replace; boundary=frame')
    reponse['Cache-Control'] = 'no-cache'
    return reponse
def video_view(request):

    camera_list=Camera.objects.filter(isOpened=True).order_by('camera_id')
    context = {
        "role": "user",
        "camera_list" : camera_list,
    }
    return render(request, 'camera.html', context)
def videoAdmin_view(request):
    camera_list=Camera.objects.all().order_by('camera_id')
    camerabackground_list = serializers.serialize("json", camera_list)
    context = {
        "role": "admin",
        "camera_list" : camera_list,
        "camerabackground_list" : camerabackground_list,
    }
    return render(request, 'camera.html', context)  

# Create your views here.
def bookhandle(request):
    camera_id=request.GET.get('camera_id')        #尋找某一個相機資料
    movedic=None
    if camera_id is None:
        movedic = Move.objects.all().order_by('-movetime')
    else:
        try:
             camera_model = Camera.objects.get(camera_id=camera_id)
             movedic=Move.objects.get(camera=camera_model).order_by('-movetime')
        except:
             movedic = Move.objects.all().order_by('-movetime')
    paginator=Paginator(movedic,20)    #每頁顯示10條
    page=request.GET.get('page')        #前段請求的頁,比如點選'下一頁',該頁以變數'page'表示
   
    try:
      move_obj=paginator.page(page) #獲取前端請求的頁數
      move_obj.adjusted_elided_pages = paginator.get_elided_page_range(page)
    except PageNotAnInteger:
        move_obj=paginator.page(1)   #如果前端輸入的不是數字,就返回第一頁
    except EmptyPage:
        move_obj=paginator.page(paginator.num_pages)   #如果前端請求的頁碼超出範圍,則顯示最後一頁.獲取總頁數,返回最後一頁.比如共10頁,則返回第10頁.
    
    return render(request, 'move.html',{'move_list':move_obj})
    # Create your views here.    
def get_videoAviToMp4(request):

    isdecode=False   #是否已經解碼
    videoUrl= request.GET.get('videoUrl')
    camera_id= request.GET.get('camera_id')
    current_user = request.user
    if current_user is None:
         return render(request, 'video.html') 
    try:
         if os.path.isfile(videoUrl):
            time=get_video_duration(videoUrl)
            if time != -1: #確認是否有長度
                isdecode=True 
    except Exception as e:
        isdecode=False
        logger.error("判斷MP4檔案發生錯誤")
    if isdecode:
        moveObj=get_moves(videoUrl)
        context = {
            'videoUrl':videoUrl,
            'camera_id':camera_id,
             'action':True,
             'moveObj':json.dumps(moveObj)

        }
        return render(request, 'video.html',context) 
    else:
        try:
            oldfile=CameraFactory.get_cameranowVideo(camera_id)
            if oldfile is not None and oldfile != videoUrl:
                os.remove(videoUrl)#不是運行中的檔案也沒有時長 所以刪除
                logger.info("不是運行中的檔案也沒有時長所以刪除"+videoUrl)
            else:
                CameraFactory.get_cameratoVideo(camera_id, True)#先暫時關閉攝影機以便讀去影片
                static="static/my_output/intime" #專門放置及時觀看影片
                # 自動建立目錄     
                if not os.path.exists(static):
                    os.makedirs(static)
                folder=static+"/"+str(current_user.id)+".mp4"
                shutil.copyfile(videoUrl, folder)
                CameraFactory.get_cameratoVideo(camera_id, False)#繼續錄製目前影片
                moveObj=get_moves(videoUrl)
                context = {
                        'videoUrl':folder,
                        'camera_id':camera_id,
                        'action':True,
                        'moveObj':json.dumps(moveObj)
                }
                return render(request, 'video.html',context)  
        except Exception as e:
            logger.error(e)
    return render(request, 'video.html') 
def get_video_duration(filename):
    #判斷時長
  cap = cv2.VideoCapture(filename)
  if cap.isOpened():
    rate = cap.get(5)
    frame_num =cap.get(7)
    duration = frame_num/rate
    return duration
  return -1
def get_moves(filename:str):
    #取得該影片偵測移動時間
    move_list=[]
    try:
        file=File.objects.get(movie=filename)
        if file is  None:
            logger.info("資料庫查無檔案:"+filename)
        else:
            moves=file.get_moves()
            if moves is not None:
                if file.starttime is None or file.endtime is None:
                    logger.info(filename+"前後時間有問題 無法取得偵測時段")
                else:
                    time=get_video_duration(filename)
                    logger.info(filename+"影片時長"+str(time))
                    logger.info(filename+"取得移動列表")
                    logger.info(filename+"開始時間:")
                    logger.info(file.starttime)
                    logger.info(filename+"結束時間:")
                    logger.info(file.endtime)
                    logger.info(filename+"移動偵測列表:")
                    start_timer=str(file.starttime)
                    head,sep,tail=start_timer.partition('.')
                    start_timer = datetime.datetime.strptime(head, r"%Y-%m-%d %H:%M:%S")
                    for move in moves:
                        end_time = str(move.movetime)
                        headend,sep,tail=end_time.partition('.')
                        end_time = datetime.datetime.strptime(headend, r"%Y-%m-%d %H:%M:%S")
                        diff = end_time - start_timer
                        move_list.append({
                        "time": diff.total_seconds(),
                        "text": str(end_time)
                        })
            else:
                logger.info(filename+"無移動列表")
    except File.DoesNotExist:
             file = None
    return move_list

def download_mp4(request):
    #解壓縮檔案提供下載
    file_path = request.GET.get('file_path')
    logger.info(file_path)
    if os.path.exists(file_path):    
            basename = os.path.basename(file_path)
        # with open(file_path, 'rb') as fh:    
        #     response = HttpResponse(fh.read(),  content_type="video/mp4")    
          
        #     response['Content-Disposition'] = \
        #     "attachment; filename=\"%s\"; filename*=utf-8''%s" % \
        #     (file_path, file_path)  
        #             return response 
                # 创建BytesIO
            s = io.BytesIO()
            
            # 使用BytesIO生成壓縮文件文件
            zip = zipfile.ZipFile(s, 'w')
            
            # 把下载文件寫入壓縮檔
            zip.write(file_path,arcname=basename)
            img1 = zip.getinfo(basename)
            # 關閉文件
            zip.close()
            # 回到初始位置，若沒設定zip會壞掉
            s.seek(0)
            
            wrapper = FileWrapper(s)
            response = HttpResponse(wrapper, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename={}.zip'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
            return response
    return HttpResponseNotFound("查無此檔案")   
def stream_video(request):
  """用響應式串流"""
  path = request.GET.get('file_path')
  return stream(request,path)
def get_cameras(request):
  """用響應式串流"""
  count = CameraFactory.returnCameraIndexes()
  print(count)
  return JsonResponse(True, safe=False)


 