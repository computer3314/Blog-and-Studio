from django.db import models

# Create your models here.
class Chat(models.Model):
    """A typical class defining a model, derived from the Model class."""
    # Metadata
    class Meta:
        verbose_name = '聊天紀錄'
        verbose_name_plural = '聊天紀錄'
    roomname =  models.TextField("聊天室",max_length = 20,blank=True,null=False)
    nickname =  models.TextField("暱稱",max_length = 20,blank=True,null=False)
    message=  models.CharField("說話內容",max_length = 200,blank=True,null=False)
    isdisable =models.BooleanField('是否可被看見',default=True)
    created_at = models.DateTimeField('新增時間',auto_now_add=True)
        # Methods
    indexes = [
        models.Index(fields=['roomname']),
    ]
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return str(self.roomname)