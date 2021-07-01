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
    interests= models.TextField('興趣', max_length=600,default='something')
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

class Education(models.Model):
    class Meta:
        verbose_name = '學歷'
        verbose_name_plural = '學歷'

    school= models.CharField('學校名稱', max_length=50)
    department = models.CharField('科系名稱', max_length=50)
    status = models.CharField('就學狀態', max_length=50)
    duringstart= models.DateField('開始時間', auto_now_add=False)
    duringsend= models.DateField('畢業時間', null=True, blank=True)
  
    def __str__(self):
        return self.school

class Skills(models.Model):
    class Meta:
        verbose_name = '專長'
        verbose_name_plural = '專長'

    skillname= models.CharField('專長名稱', max_length=50)
    skillcontect = models.TextField('專長描述', max_length=600)
    skilltag = models.CharField('專長標籤', max_length=200)
    def __str__(self):
        return self.skillname

class Projects(models.Model):
    class Meta:
        verbose_name = '專案成就'
        verbose_name_plural = '專案成就'

    projectname= models.CharField('專案名稱', max_length=50)
    projectstart = models.DateField('開始時間', auto_now_add=False)
    projectend = models.DateField('結束時間', null=True, blank=True)
    projectcontent = models.TextField('專案描述', max_length=600)
    projecturl=models.URLField('專案連結',blank=True)
    projectimg=models.ImageField('專案圖片',blank=True,upload_to='static/assets/img')
    def __str__(self):
        return self.projectname

class Awards(models.Model):
    class Meta:
        verbose_name='獎項與名稱'
        verbose_name_plural='獎項與名稱'
    awardname=models.CharField('獎項與名稱',max_length=50)
    awarddate= models.DateField('獲獎日', null=True, blank=True)
    def __str__(self):
        return self.awardname

