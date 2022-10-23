from django.http import HttpResponse
from django.shortcuts import render
from django.http import StreamingHttpResponse
from .cameras import CameraFactory, BaseCamera
from django.conf import settings
def gen_display(camera: BaseCamera):
    """
   影片生成器。
    """
    while True:
        # 读取图片
        frame = camera.get_frame(None)
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_displayAdmin(camera: BaseCamera):
    """
   影片生成器。
    """
    while True:
        # 读取图片
        frame = camera.get_frame("admin")
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
    camera: BaseCamera = CameraFactory.get_camera(camera_id)
    #使用流傳輸傳輸影片流
    if(camera is None):
         return HttpResponse(content='該相機不存在或已經暫停！ ', status=200)
    return StreamingHttpResponse(gen_display(camera), content_type='multipart/x-mixed-replace; boundary=frame')
def videoAdmin(request):
    """
    影片流路由。將其放入img標記的src屬性中。
    例如：<img src='https://ip:port/uri' >
    """
    # 影片相機對象
    camera_id = request.GET.get('camera_id')
    camera: BaseCamera = CameraFactory.get_camera(camera_id)
    if(camera is None):
         return HttpResponse(content='該相機不存在或已經暫停！ ', status=200)
    #使用流傳輸傳輸影片流
    return StreamingHttpResponse(gen_displayAdmin(camera), content_type='multipart/x-mixed-replace; boundary=frame')
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
        "url" : settings.PRO_HOST+"api/cameraAdmin/?camera_id=1",
        "camera_id": "1"
    }
    return render(request, 'camera.html', context)  
    