 # chat/views.py
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
def index(request):
     return render(request, 'chat/index.html', {})
@xframe_options_exempt
def room(request, room_name):
     nick_name = request.GET.get('nickname')
     if nick_name is None:
          nick_name=""
     return render(request, 'chat/room.html', {
         'room_name': room_name,
         'nick_name': nick_name
     })