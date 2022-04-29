from django.contrib import admin
from .models import stock
# Register your models here.
class stockAdmin(admin.ModelAdmin):
    list_display = ('stock_id', 'stock_date', 'buy_date', 'stock_name', 'open', 'high', 'low', 'close', 'Increase','buy','self')
    search_fields = ('stock_id', 'stock_date', 'buy_date', 'stock_name', 'open', 'high', 'low', 'close', 'Increase','buy','self')


admin.site.register(stock, stockAdmin)