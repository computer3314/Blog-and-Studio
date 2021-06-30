from django.db import models
from PIL import Image
# Create your models here.
class About(models.Model):
    class Meta:
        verbose_name = '使用者資料'
        verbose_name_plural = '使用者資料'
    name = models.CharField('姓名', max_length=30,default='陳昜睿')
    introduction = models.TextField('自我介紹', max_length=1000)
    photo = models.ImageField('大頭貼',blank=True,)
    mail = models.CharField('電子信箱', max_length=100)
    phone = models.CharField('手機', max_length=100)
    address = models.CharField('地址', max_length=100)
    twitterid = models.CharField('推特ID', max_length=100)
    fbid = models.CharField('臉書ID', max_length=100)
    igid = models.CharField('IG', max_length=100)
    githubid = models.CharField('github', max_length=100)
    def __str__(self):
        return self.name
