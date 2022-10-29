from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from task.task import TaskFactory
from django.http import JsonResponse
from camera.models import Camera

import importlib
#這邊觸發排程服務
TaskFactory.get_scheduler()


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
def delete_file(request):
   
   cameras = Camera.objects.all()
   print(cameras)
  #判斷過期檔案
def shouldkeep(file,Dday):
     if datetime.datetime.fromtimestamp( os.path.getmtime(file) ) > \
        datetime.datetime.now() - datetime.timedelta(Dday):
        return True
    #刪除檔案
def _removeold(outputFolder):
        for i in os.walk(outputFolder):
            for j in i[2]:
                if not shouldkeep(os.path.join(i[0],j)):
                 os.remove( os.path.join(i[0],j) )
        


