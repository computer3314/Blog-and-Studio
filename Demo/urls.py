"""Demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from post.views import aboutget
from camera.views import video,video_view,videoAdmin_view,bookhandle,get_videoAviToMp4,download_mp4
from django .contrib.auth.decorators import login_required
from task.task import TaskFactory
import sys
#引入排程包
from task.views import job_add_task,job_del_task,job_pause_task,job_resume_task,job_list_task
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', aboutget),
    path('api/camera/', video),
    path('camera', video_view),
    path('job/add/', login_required(job_add_task)),
    path('job/del/', login_required(job_del_task)),
    path('job/pause/', login_required(job_pause_task)),
    path('job/resume/', login_required(job_resume_task)),
    path('job/list', login_required(job_list_task)),
    path('getvideo', login_required(get_videoAviToMp4)),
    path('downloadmp4/', login_required(download_mp4)),
    path('cameraAdmin', login_required(videoAdmin_view)),  
    re_path(r'^move', login_required(bookhandle), name="move")                                         
]
#這邊觸發Server執行後動作
RUNNING_DEVSERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')
if RUNNING_DEVSERVER:
 #排程服務器
 TaskFactory.get_scheduler()
 #Server啟動後執行
 TaskFactory.init()
