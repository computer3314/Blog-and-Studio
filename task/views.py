from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from task.task import TaskFactory
from django.http import JsonResponse
from camera.models import Camera
import importlib
import os
import datetime
from camera.cameras import CameraFactory, BaseCamera
def job_add_task(request):
    # 給前端新增
    job_id=request.GET.get('job_id')
    cron=request.GET.get('cron')
    function_string = job_id
    mod_name, func_name = function_string.rsplit('.',1)
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    add=TaskFactory.add_task(func,job_id,cron)
    return JsonResponse(add, safe=False)
def job_del_task(request):
    #刪除JOB
    job_id=request.GET.get('job_id')
    return JsonResponse(TaskFactory.del_task(job_id), safe=False)
def job_pause_task(request):
    #暫停JOB
    job_id=request.GET.get('job_id')
    return JsonResponse(TaskFactory.pause_task(job_id), safe=False)
def job_resume_task(request):
    #恢復job
    job_id=request.GET.get('job_id')
    return JsonResponse(TaskFactory.resume_task(job_id), safe=False)
def job_list_task(request):
    #job列表
    return JsonResponse(TaskFactory.getTasks(), safe=False)
  #判斷過期檔案
def delete_file():
    #固定刪除檔案程式，寫成排程每日固定刪除
    # 輸出目錄
   outputBaseFolder = "static/my_output/"
   cameras = Camera.objects.all()
   print("刪除過期檔案排程啟動")
   for camera in cameras:
    outputFolder=outputBaseFolder+camera.title+"/"
    outputVideoFolder=outputBaseFolder+camera.title+"video/"
    print("圖片檔資料夾:"+str(outputFolder))
    print("圖片檔過期天數:"+str(camera.dday))
    _removeold(outputFolder,camera.dday)
    print("影片檔資料夾:"+str(outputVideoFolder))
    print("影片檔過期天數:"+str(camera.videodday))
    _removeold(outputVideoFolder,camera.videodday)
   print("刪除過期檔案排程結束")
  #判斷過期檔案
def shouldkeep(file,Dday):
     if datetime.datetime.fromtimestamp( os.path.getmtime(file) ) > \
        datetime.datetime.now() - datetime.timedelta(Dday):
        return True
    #刪除檔案
def _removeold(outputFolder,Dday):
        count=0
        for i in os.walk(outputFolder):     
            for j in i[2]:
                if not shouldkeep(os.path.join(i[0],j),Dday):
                 print(os.path.join(i[0],j))
                 os.remove( os.path.join(i[0],j) )
                 count+=1
        print("資料夾:"+outputFolder+"已刪除了  "+str(count)+"  筆過期資料")
def update_ALLcamera():
    print("排程固定更新所有相機開始")
    CameraFactory.update_ALLcamera()
    print("排程固定更新所有相機結束")


        


