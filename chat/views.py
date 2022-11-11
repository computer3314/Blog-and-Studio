 # chat/views.py
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import Chat
from django.http import JsonResponse
from dbcheck import db_retry
def index(request):
     return render(request, 'chat/index.html', {})
@xframe_options_exempt
def room(request, room_name):
     nick_name = request.GET.get('nickname')
     if nick_name is None:
          nick_name=""
     messages = Chat.objects.filter(roomname = room_name)
     total_msgs = len(messages)
     if total_msgs > 25:
          last_msgs = messages[total_msgs-25::]
     else:
          last_msgs = messages
     return render(request, 'chat/room.html', {
         'room_name': room_name,
         'nick_name': nick_name,
         'messages': last_msgs
     })
@xframe_options_exempt
def deletemessage(request):
     data=request.GET.getlist('data[]')
     try:
          for message in data:
               db_retry(Chat.objects.filter(id=int(message)).update(isdisable=False))
          res=dict({"response":True,"datas":data})
     except:
          res=dict({"response":False})
     return JsonResponse(res, safe=False)
