使用Python框架Django 為自己打造一個個人展示網站!
<br/>
網站:<url>https://happy.shengda.codes</url>
<br/>
#在static目錄下新增套件<br/>
npm install <br/>
npm install videojs-markers-plugin<br/>
npm install jquery popper.js --save<br/>
npm install bootstrap@v5.2.2      <br/>
npm install jquery   <br/>
npm install --save videojs-landscape-fullscreen<br/>
npm i jquery-contextmenu  右鍵選單<br/>
timeout':60,<br/>
#將固定刪除排程資料庫LOG加入排程中<br/>
job/add/?job_id=task.views.delete_file&cron=30 1 * * * 每天1點檢查刪除過期檔案<br/>
job/add/?job_id=task.management.commands.runaps.delete_old_job_executions&cron=0 2 * * MON 每周一刪除排程過期LOG<br/>
job/add/?job_id=task.views.update_ALLcamera&cron= 0 * * * * 每一小時更新相<br/>
python manage.py makemigrations<br/>
python manage.py migrate      <br/>
進行makemigrations <br/>
python -m daphne -b 0.0.0.0 -p 8001 Demo.asgi:application #啟動websocket   8001port<br/>
python manage.py runserver --noreload 127.0.0.1:8000<br/>
<br>
1:個人部落格<br/>
2:網路攝影機，使用opencv套件偵測動物動作，並且發送信件<br/>
3:攝影機直播聊天室<br/>
