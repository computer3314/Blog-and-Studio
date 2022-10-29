from django.http import HttpResponse
from django.shortcuts import render
from django.http import StreamingHttpResponse
from .cameras import CameraFactory, BaseCamera,BaseVideo
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators import gzip
from PIL import Image,ImageSequence
import numpy as np
import cv2
import time
from .models import Move

from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
def gen_videodisplay(video: BaseVideo):
    """
    影片生成器
    """
    while True:
        # 读取图片
        try:
            frame = video.get_frame()
            if frame is not None:
                # 鍵盤輸入空格暫停，輸入q退出
                key = cv2.waitKey(1) & 0xff

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            print("影片播放完畢")
    print("影片播放完畢")
def gen_display(camera: BaseCamera,role):
    """
   直播影片生成器。
    """
    img_list=CameraFactory.loadingpic()
    if camera is None or camera.cam is None:
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
    if role is None:
        role="None"
    camera: BaseCamera = CameraFactory.get_camera(camera_id)
    #使用流傳輸傳輸影片流
    reponse=StreamingHttpResponse(gen_display(camera,role), content_type='multipart/x-mixed-replace; boundary=frame')
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
        "url" : settings.PRO_HOST+"api/camera/?camera_id=1&role=admin",
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

def get_video(request):
    return render(request, 'video.html')  
   
 