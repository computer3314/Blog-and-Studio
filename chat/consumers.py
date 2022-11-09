import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import datetime
 
 
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
         message = text_data_json['message']
         nickname = text_data_json['nickname']
         # 發送消息到頻道組，頻道組調用chat_message方法
         async_to_sync(self.channel_layer.group_send)(
             self.room_group_name,
             {
                 'type': 'chat_message',
                 'message': message,
                 'nickname': nickname
             }
         )
 
     # 從頻道收到訊息後執行方法
     def chat_message(self, event):
         message = event['message']
         datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         nickname = event['nickname']
         # 通過websocket發送消息到客户端
         self.send(text_data=json.dumps({
             'message': f'{nickname}=>{message}'
         }))