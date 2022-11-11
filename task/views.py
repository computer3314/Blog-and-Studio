from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from task.task import TaskFactory
from django.http import JsonResponse
from camera.models import Camera,File,Move
from chat.models import Chat
import importlib
import os
from camera.cameras import CameraFactory, BaseCamera
from datetime import datetime, timedelta
import logging
from dbcheck import db_retry
# Get an instance of a logger
logger = logging.getLogger(__name__)
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
def job_run_once(request):
    #執行一次job
    job_id=request.GET.get('job_id')
    function_string = job_id
    mod_name, func_name = function_string.rsplit('.',1)
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    return JsonResponse(TaskFactory.run_once(func,job_id), safe=False)
    
def job_list_task(request):
    #job列表
    return JsonResponse(TaskFactory.getTasks(), safe=False)
  #判斷過期檔案
def delete_file():
    #固定刪除檔案程式，寫成排程每日固定刪除
    # 輸出目錄
   outputBaseFolder = "static/my_output/"
   cameras = Camera.objects.all()
   logger.info("刪除過期檔案排程啟動")
   for camera in cameras:
    outputFolder=outputBaseFolder+camera.title+"/"
    outputVideoFolder=outputBaseFolder+camera.title+"video/"
    logger.info("圖片檔資料夾:"+str(outputFolder))
    logger.info("圖片檔過期天數:"+str(camera.dday))
    _removeold(outputFolder,camera.dday)
    logger.info("影片檔資料夾:"+str(outputVideoFolder))
    logger.info("影片檔過期天數:"+str(camera.videodday))
    _removeold(outputVideoFolder,camera.videodday)
    db_retry(Move.objects.filter(created_at__lte=datetime.now()-timedelta(days=int(camera.dday)),camera=camera).delete())
    logger.info("刪除超過" + str(camera.dday) + "天移動偵測資料庫資料")
    db_retry(File.objects.filter(created_at__lte=datetime.now()-timedelta(days=int(camera.videodday)),camera=camera).delete())
    logger.info("刪除超過" + str(camera.videodday) + "天影片檔資料庫資料")

   db_retry(Chat.objects.filter(created_at__lte=datetime.now()-timedelta(days=int(1))).delete())
   logger.info("刪除全部超過" + str(1) + "天聊天室資料庫資料")
   logger.info("刪除過期檔案排程結束")
  #判斷過期檔案
def shouldkeep(file,Dday):
     if datetime.fromtimestamp( os.path.getmtime(file) ) > \
        datetime.now() - timedelta(Dday):
        return True
    #刪除檔案
def _removeold(outputFolder,Dday):
        count=0
        for i in os.walk(outputFolder):     
            for j in i[2]:
                if not shouldkeep(os.path.join(i[0],j),Dday):
                 logger.info(os.path.join(i[0],j))
                 os.remove( os.path.join(i[0],j) )
                 count+=1
        logger.info("資料夾:"+outputFolder+"已刪除了  "+str(count)+"  筆過期資料")
def update_ALLcamera():
    logger.info("排程固定更新所有相機開始")
    CameraFactory.update_ALLcamera()
    logger.info("排程固定更新所有相機結束")

    


        


