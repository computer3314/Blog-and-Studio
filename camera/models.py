import queue
import threading

import cv2
from django.db import models

class Camera(models.Model):
    """A typical class defining a model, derived from the Model class."""
    # Metadata
    class Meta:
        verbose_name = '攝影機'
        verbose_name_plural = '攝影機'
    camera_id = models.TextField('攝影機編號', max_length=100,blank=True,unique=True)
    camera_url = models.TextField('攝影機位置', max_length=100,default='0',blank=True)
    title = models.CharField('標題', max_length=20,default='test')
    width = models.IntegerField('螢幕寬度', default=1280,blank=True)
    heigth = models.IntegerField('螢幕高度', default=720,blank=True)
    fps = models.IntegerField('預設幀數', default=30,blank=True)
    fast = models.IntegerField('移動偵測靈敏度', default=25,blank=True)
    dday = models.IntegerField('固定刪除截圖檔案時間(天數)', default=7,blank=True)
    videodday = models.IntegerField('固定刪除影片檔案時間(天數)', default=3,blank=True)
    moveNotice = models.IntegerField('移動偵測通知時間(秒數)', default=60,blank=True)
    mailCheck=models.BooleanField('是否移動發信',default=True)
    scancheck=models.BooleanField('是否移動截圖',default=True)
    videocheck=models.BooleanField('是否連續錄製',default=True)
    isOpened=models.BooleanField('是否啟動',default=True)
    # Methods
    def camera_api(self):
        """Returns the URL to access a particular instance of MyModelName."""
        return int(self.camera_url)
        # Methods
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.title
class Move(models.Model):
    """A typical class defining a model, derived from the Model class."""
    # Metadata
    class Meta:
        verbose_name = '移動偵測'
        verbose_name_plural = '移動偵測'
    camera_id = models.TextField('攝影機編號', max_length=100,blank=True)
    movetime= models.DateTimeField('移動時間',auto_now=True)
    photo = models.ImageField('移動截圖',blank=True,upload_to='static/my_output', null=True)
    created_at = models.DateTimeField('新增時間',auto_now_add=True)
        # Methods
    def camera_api(self):
        """Returns the URL to access a particular instance of MyModelName."""
        camera_model = Camera.objects.get(camera_id=self.camera_id)
        return camera_model
        # Methods
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.camera_id
