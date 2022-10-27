# runapscheduler.py
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util



#開始排程服務(背景執行，最好是不會變動的排程在使用次Common  觸發方法python manage.py runaps)
def my_job():
  print("myjob")
  pass


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way. 
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
  """
  此作業從數據庫中刪除早於“max_age”的 APScheduler 作業執行條目。
  它有助於防止數據庫填滿不存在的舊曆史記錄
  更有用。
  
  :param max_age：保留歷史作業執行記錄的最長時間。
                  默認為 7 天。
  """
  DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
  help = "Runs APScheduler."

  def handle(self, *args, **options):
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
      my_job,
      trigger=CronTrigger(second="*/10"),  # Every 10 seconds
      id="my_job",  # The `id` assigned to each job MUST be unique
      max_instances=1,
      replace_existing=True,
    )
    print("Added job 'my_job'.")

    scheduler.add_job(
      delete_old_job_executions,
      trigger=CronTrigger(
        day_of_week="mon", hour="00", minute="00"
      ),  # Midnight on Monday, before start of the next work week.
      id="delete_old_job_executions",
      max_instances=1,
      replace_existing=True,
    )
    print(
      "Added weekly job: 'delete_old_job_executions'."
    )

    try:
      print("Starting scheduler...")
      scheduler.start()
    except KeyboardInterrupt:
      print("Stopping scheduler...")
      scheduler.shutdown()
      print("Scheduler shut down successfully!")