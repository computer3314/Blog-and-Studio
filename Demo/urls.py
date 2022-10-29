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
from camera.views import video,video_view,videoAdmin_view,bookhandle,get_video
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
    path('job/add/', job_add_task),
    path('job/del/', job_del_task),
    path('job/pause/', job_pause_task),
    path('job/resume/', job_resume_task),
    path('job/list', job_list_task),
    path('video', get_video),
    path('cameraAdmin', login_required(videoAdmin_view)),  
    re_path(r'^move', login_required(bookhandle), name="move")                                         
]
#這邊觸發Server執行後動作
RUNNING_DEVSERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')
if RUNNING_DEVSERVER:
 #排程服務器
 TaskFactory.get_scheduler()
 #Server啟動後執行
 #TaskFactory.init()
