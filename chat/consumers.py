import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import datetime
from .models import Chat
from dbcheck import db_retry
from django.core import serializers
class ChatConsumer(WebsocketConsumer):
     # websocket建立連接時執行方法
     def connect(self):
         #從url裡獲取聊天室名字，為每個房間建立一個頻道組
         self.room_name = self.scope['url_route']['kwargs']['room_name']
         self.room_group_name = 'chat_%s' % self.room_name
 
         # 將當前頻道加入頻道組
         async_to_sync(self.channel_layer.group_add)(
             self.room_group_name,
             self.channel_name
         )
 
         # 接受所有websocket请求
         self.accept()
 
     # websocket斷開時執行方法
     def disconnect(self, close_code):
         async_to_sync(self.channel_layer.group_discard)(
             self.room_group_name,
             self.channel_name
         )
 
     # 從websocket接收到消息時執行函數
     def receive(self, text_data):
         text_data_json = json.loads(text_data)
         Type = text_data_json['type']
         if Type == 'chat_message':
            try:
                message = text_data_json['message']
                nickname = text_data_json['nickname']
                chat=db_retry(Chat.objects.create(roomname=self.room_name,nickname=nickname,message=message))
                # 發送消息到頻道組，頻道組調用chat_message方法
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': Type,
                        'id': f'{chat.id}',
                        'roomname': f'{chat.roomname}',
                        'nickname': f'{chat.nickname}',
                        'message': f'{chat.message}',
                        'time': f'{chat.created_at}'
                    }
                )
            except Chat.DoesNotExist:
            # Exception thrown when the .get() function does not find any item.
              pass  # Handle the exception here. 
         elif Type == 'delete_message':
            delmessages = text_data_json['messages']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': Type,
                    'messages': delmessages,
                }
            )
 
     # 從頻道收到訊息後執行方法
     def chat_message(self, event):
         id = event['id']
         roomname = event['roomname']
         nickname = event['nickname']
         message = event['message']
         time = event['time']
         Type = event['type']
            # 通過websocket發送消息到客户端
         self.send(text_data=json.dumps({
                'type': f'{Type}',
                'id': f'{id}',
                'roomname': f'{roomname}',
                'nickname': f'{nickname}',
                'message': f'{message}',
                'time': f'{time}'
            }))

    # 從頻道收到刪除訊息後執行方法
     def delete_message(self, event):
         messages = event['messages']
         Type = event['type']
         try:
            # 通過websocket發送消息到客户端
            self.send(text_data=json.dumps({
                'type': f'{Type}',
                'messages': f'{messages}',
            }))
         except Chat.DoesNotExist:
            # Exception thrown when the .get() function does not find any item.
            pass  # Handle the exception here. 