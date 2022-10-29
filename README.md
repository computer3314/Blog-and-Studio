使用Python框架Django 為自己打造一個個人展示網站!
#將固定刪除排程資料庫LOG加入排程中
job/add/?job_id=task.views.delete_file&cron=0 1 * * *  每天1點檢查刪除過期檔案
job/add/?job_id=task.management.commands.runaps.delete_old_job_executions&cron=0 2 * * MON 每周一刪除排程過期LOG
job/add/?job_id=task.views.update_ALLcamera&cron=0 0 * * * 每天0點更新所有相機
npm install --save-dev video.js
python manage.py makemigrations
python manage.py migrate      
進行makemigrations 