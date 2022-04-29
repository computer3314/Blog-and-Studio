from django.db import models

# Create your models here.
class stock(models.Model):
    class Meta:
        verbose_name = '股票'
        verbose_name_plural = '股票'
    stock_id = models.CharField('證券代號', max_length=30)
    stock_date= models.CharField('日期', max_length=30)
    buy_date= models.CharField('買超日期', max_length=30)
    stock_name = models.CharField('證券名稱',max_length=30)
    open = models.DecimalField('開盤價',max_digits=5, decimal_places=2, blank=True, null=True)
    high = models.DecimalField('最高點',max_digits=5, decimal_places=2, blank=True, null=True)
    low = models.DecimalField('最低點',max_digits=5, decimal_places=2, blank=True, null=True)
    close = models.DecimalField('收盤價',max_digits=5, decimal_places=2, blank=True, null=True)
    Increase = models.DecimalField('當日漲幅',max_digits=5, decimal_places=2, blank=True, null=True)
    buy = models.CharField('第二天買入價格', max_length=100,blank=True,default='')
    self = models.CharField('第三天賣出價格', max_length=100,blank=True,default='')
    def __str__(self):
        return self.stock_name
