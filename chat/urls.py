 # chat/urls.py
from django.urls import path
from . import views
 
urlpatterns = [
     #path('', views.index, name='index'),  #輸入聊天名字的  不需要
     path('<str:room_name>/', views.room, name='room'),
 ]