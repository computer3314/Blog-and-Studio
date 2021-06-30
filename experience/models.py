from django.db import models

# Create your models here.
class Experience(models.Model):
    class Meta:
        verbose_name = '工作經驗'
        verbose_name_plural = '工作經驗'

    companyname= models.CharField('公司名稱', max_length=100)
    position = models.CharField('職位', max_length=50)
    content = models.TextField('工作內容', max_length=600)
    start= models.DateField('工作時間起', auto_now_add=False)
    end= models.DateField('工作時間迄', auto_now_add=False)
  
    def __str__(self):
        return self.companyname