使用Python框架Django 為自己打造一個個人展示網站!
#在static目錄下新增套件
npm install 
npm install videojs-markers-plugin
npm install jquery popper.js --save
npm install bootstrap@v5.2.2      
npm install jquery   
npm install --save videojs-landscape-fullscreen
npm i jquery-contextmenu  右鍵選單
timeout':60,
#將固定刪除排程資料庫LOG加入排程中
job/add/?job_id=task.views.delete_file&cron=30 1 * * * 每天1點檢查刪除過期檔案
job/add/?job_id=task.management.commands.runaps.delete_old_job_executions&cron=0 2 * * MON 每周一刪除排程過期LOG
job/add/?job_id=task.views.update_ALLcamera&cron= 0 * * * * 每一小時更新相機
python manage.py makemigrations
python manage.py migrate      
進行makemigrations 
python -m daphne -b 0.0.0.0 -p 8001 Demo.asgi:application #啟動websocket   8001port
python manage.py runserver --noreload 127.0.0.1:8000