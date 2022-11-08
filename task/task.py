from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from apscheduler.schedulers.blocking import BlockingScheduler
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
from django.conf import settings
import time
from apscheduler.triggers.cron import CronTrigger
from django.core import serializers
import json
from camera.cameras import CameraFactory, BaseCamera
import logging
import datetime
# Get an instance of a logger
logger = logging.getLogger(__name__)
class TaskFactory:
    """
    任務工廠
    """
    # 存儲實例化的所有任務
    scheduler=None
    
    @classmethod
    def get_scheduler(cls):
      if cls.scheduler is None:
        cls.scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        cls.scheduler.add_jobstore(DjangoJobStore(), "default")
        register_events(cls.scheduler)
        cls.scheduler.start()
      logger.info("取得排程物件")
    @classmethod
    def getTasks(cls):
      if cls.scheduler is None:
             cls.get_scheduler()
      schedules = []
      newJob=dict()
      isrun = True
      for job in cls.scheduler.get_jobs():
        if job.next_run_time is None:
            isrun=False
        else:
           isrun=True
        newJob=dict({"job_id": str(job.id), "job_name": str(job.name), "job_trigger": str(job.trigger)
        , "job_isrun": str(isrun), "job_next_run_time ": str(job.next_run_time )}) 
        schedules.append(newJob)
      logger.info("取得排程列表")
      return schedules
    
    @classmethod
    def add_task(cls,func,func_ID,cron):
      #新增任務
        try:
            if cls.scheduler is None:
             cls.get_scheduler()
            Trigger=CronTrigger.from_crontab(cron)
            #Trigger=CronTrigger(second="*/5")
            cls.scheduler.add_job(
            func,
            trigger=Trigger,  # cron表達式
            id=func_ID,  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
          )
            logger.info("ID:"+ func_ID +" 新增成功")
            return True
        except Exception as e:
            logger.error("ID:"+ func_ID +" 新增失敗")
            print(e)
            return None
    @classmethod
    def del_task(cls,func_ID):
        try:
          #刪除任務
            if cls.scheduler is None:
             cls.get_scheduler()

            cls.scheduler.remove_job(func_ID)
            logger.info("ID:"+ func_ID +" 刪除成功")
            return True
        except Exception as e:
            logger.error("ID:"+ func_ID +" 刪除失敗")
            print(e)
            return None
    @classmethod
    def resume_task(cls,func_ID):
      #恢復任務
        try:
            if cls.scheduler is None:
             cls.get_scheduler()
            cls.scheduler.resume_job(func_ID)
            logger.info("ID:"+ func_ID +"恢復成功")
            return True
        except Exception as e:
            logger.error("ID:"+ func_ID +"恢復失敗")
            print(e)
            return None
    @classmethod
    def pause_task(cls,func_ID):
      #暫停任務
        try:
            if cls.scheduler is None:
             cls.get_scheduler()
            cls.scheduler.pause_job(func_ID)
            logger.info("ID:"+ func_ID +"  暫停成功")
            return True
        except Exception as e:
            logger.error("ID:"+ func_ID +"  pause失敗")
            print(e)
            return None
    @classmethod
    def run_once(cls,func,func_ID):
      #恢復執行一次
        try:
            if cls.scheduler is None:
             cls.get_scheduler()
            cls.scheduler.add_job(func,'date', run_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logger.info("ID:"+ func_ID +"執行成功")
            return True
        except Exception as e:
            logger.error("ID:"+ func_ID +"執行失敗")
            print(e)
            return None
    @classmethod
    def init(cls):
      logger.info("啟動程式自動開啟")
      CameraFactory.update_ALLcamera()



        