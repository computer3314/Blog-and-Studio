from django.db import models
from PIL import Image
# Create your models here.
class Post(models.Model):
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'

    title = models.CharField('標題', max_length=20, )
    content = models.TextField('內容', max_length=200)
    
    def __str__(self):
        return self.title

# Create your models here.
class About(models.Model):
    class Meta:
        verbose_name = '使用者資料'
        verbose_name_plural = '使用者資料'
    name = models.CharField('姓名', max_length=30,default='陳昜睿')
    introduction = models.TextField('自我介紹', max_length=1000)
    photo = models.ImageField('大頭貼',blank=True,upload_to='static/assets/img')
    mail = models.CharField('電子信箱', max_length=100)
    phone = models.CharField('手機', max_length=100)
    address = models.CharField('地址', max_length=100)
    twitterid = models.CharField('推特ID', max_length=100)
    fbid = models.CharField('臉書ID', max_length=100)
    igid = models.CharField('IG', max_length=100)
    githubid = models.CharField('github', max_length=100)
    def __str__(self):
        return self.name

class Experience(models.Model):
    class Meta:
        verbose_name = '工作經驗'
        verbose_name_plural = '工作經驗'

    companyname= models.CharField('公司名稱', max_length=100)
    position = models.CharField('職位', max_length=50)
    content = models.TextField('工作內容', max_length=600)
    start= models.DateField('工作時間起', auto_now_add=False)
    end= models.DateField('工作時間迄', null=True, blank=True)
  
    def __str__(self):
        return self.companyname

class Experience(models.Model):
    class Meta:
        verbose_name = '工作經驗'
        verbose_name_plural = '工作經驗'

    companyname= models.CharField('公司名稱', max_length=100)
    position = models.CharField('職位', max_length=50)
    content = models.TextField('工作內容', max_length=600)
    start= models.DateField('工作時間起', auto_now_add=False)
    end= models.DateField('工作時間迄', null=True, blank=True)
  
    def __str__(self):
        return self.companyname
