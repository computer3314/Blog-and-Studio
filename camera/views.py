from django.http import HttpResponse
from django.shortcuts import render
from django.http import StreamingHttpResponse
from .cameras import CameraFactory, BaseCamera
from django.conf import settings
from PIL import Image,ImageSequence
import numpy as np
import cv2
import time
from .models import Move
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
def gen_display(camera: BaseCamera,role):
    """
   影片生成器。
    """
    if camera is None or camera.cam is None or (camera.isstop):
        ##沒讀到影片loding
        loadingPic="static/photo/loading.gif"
        img_list = []  
        
        gif = Image.open(loadingPic)                # 讀取動畫圖檔
        
        gif.resize((30, 30), Image.ANTIALIAS)
        for frame in ImageSequence.Iterator(gif):
         frame = frame.convert('RGB')    
         opencv_img = np.array(frame, dtype=np.uint8)   # 轉換成 numpy 陣列
         opencv_img = cv2.cvtColor(opencv_img, cv2.COLOR_RGBA2BGRA)  # 顏色從 RGBA 轉換為 BGRA
         cv2.rectangle(opencv_img,(100,120),(300,180),(0,0,0),-1)
         img_list.append(opencv_img)                    # 利用串列儲存該圖片資訊
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
    return StreamingHttpResponse(gen_display(camera,role), content_type='multipart/x-mixed-replace; boundary=frame')
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
    