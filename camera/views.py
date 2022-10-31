from django.http import HttpResponse
from django.shortcuts import render
from django.http import StreamingHttpResponse
from .cameras import CameraFactory, BaseCamera
from django.http import JsonResponse
from django.conf import settings
from PIL import Image,ImageSequence
import numpy as np
import cv2
import time
from .models import Move,Camera
import os
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from moviepy.editor import *
import shutil
def gen_display(camera: BaseCamera,role,background:bool):
    """
   直播影片生成器。
    """
    img_list=CameraFactory.loadingpic()
    if (camera is None or camera.cam is None) and background is not True:
        while True:
         for i in img_list:
            time.sleep(0.1)
            img = cv2.resize(i, (0, 0), fx=0.25, fy=0.25)
            ret, jpeg = cv2.imencode('.jpeg', img)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    else:
        while True:
            frame = camera.get_frame(role)
            if frame is not None:     
                if background is True:
                     #網頁背景執行，比較不會斷線
                    frame = str(time.time()).encode("utf-8")
                    yield (b'--frame\r\n'
                                b'Content-Type: text/plain;charset=utf-8\r\n\r\n' + frame + b'\r\n\r\n')  
                else:
                     #網頁前端執行，http有時候會斷開
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
            else:
                break
        print("影片播放完畢")
        while True:
             for i in img_list:
                    time.sleep(0.1)
                    img = cv2.resize(i, (0, 0), fx=0.25, fy=0.25)
                    ret, jpeg = cv2.imencode('.jpeg', img)
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
                
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
    reponse=StreamingHttpResponse(gen_display(camera,role,background), content_type='multipart/x-mixed-replace; boundary=frame')
    reponse['Cache-Control'] = 'no-cache'
    return reponse
def video_view(request):
    context = {
        "role": "user",
        "website": {
            "domain": settings.PRO_HOST,
        },
        "url" : settings.PRO_HOST+"api/camera/?camera_id=1",
        "camera_id": "1"
    }
    return render(request, 'camera.html', context)
def videoAdmin_view(request):
    context = {
        "role": "admin",
        "website": {
            "domain": settings.PRO_HOST,
        },
        "url" : settings.PRO_HOST+"api/camera/?camera_id=1",
        "urlbackground" : settings.PRO_HOST+"api/camera/?camera_id=1&role=admin&background=True",
        "camera_id": "1"
    }
    return render(request, 'camera.html', context)  

# Create your views here.
def bookhandle(request):
    movedic = Move.objects.all().order_by('-movetime')
    paginator=Paginator(movedic,10)    #每頁顯示2條
    page=request.GET.get('page')        #前段請求的頁,比如點選'下一頁',該頁以變數'page'表示
    try:
      move_obj=paginator.page(page) #獲取前端請求的頁數
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
            fn2 = videoUrl[0:-4]+'_convert.mp4'   
            if os.path.isfile(fn2):  
                videoUrl=fn2
                isdecode=True   
    except Exception as e:
        print("尚未解碼")
        isdecode=False
    if isdecode:
        context = {
            'videoUrl':videoUrl,
            'camera_id':camera_id,
        }
        return render(request, 'video.html',context) 
    else:
        try:
            CameraFactory.get_cameratoVideo(camera_id, True)#先暫時關閉攝影機以便讀去影片
            video = VideoFileClip(videoUrl)    # 讀取影片     
            output = video.copy() #複製目前檔案
            fn2 = videoUrl[0:-4]+'_convert.mp4'     
            output.write_videofile(fn2,temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac") #重新編碼 讓瀏覽器可以看
            context = {
                    'videoUrl':fn2,
                    'camera_id':camera_id,
            }
            CameraFactory.get_cameratoVideo(camera_id, False)#繼續錄製目前影片
            return render(request, 'video.html',context)  
        except Exception as e:
            CameraFactory.get_cameratoVideo(camera_id, False)
            print(e)

    return render(request, 'video.html') 


 