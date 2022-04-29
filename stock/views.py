from django.shortcuts import render
import requests
from io import StringIO
import pandas as pd
import numpy as np
import json
from django.shortcuts import HttpResponse
from datetime import datetime
import datetime
import time
from twstock import Stock
import twstock
from .models import stock
def getnewday():
    today=datetime.datetime.now()
    week=today.weekday()
    closetime=time.strftime('%H', time.localtime())
    count=0
    if int(closetime) <16:
        today= today + datetime.timedelta(days  = -1)
        week=today.weekday()
    if week == 6:
       today=(today+datetime.timedelta(days=-2)).strftime("%Y%m%d")
       count+=1
    elif week == 5:
       today=(today+datetime.timedelta(days=-1)).strftime("%Y%m%d")
       
  
    
    else:
       today=today.strftime("%Y%m%d")

    #today="20210703"
    return today
def stock_views(request,p1): 
    today=getnewday()
    today=str(int(today[0:4])-1911 )+"/"+str(today[4:6])+"/"+str(today[6:8])
    stock_no=p1
    try: 
         date_list =  stock.objects.filter(stock_id=stock_no).order_by('-stock_date')
        
    except:
          errormessage1 = " (讀取錯誤!)"
 
 


    return render(request, "post_detail.html",locals())

def transform_date(date):
        y, m, d = date.split('/')
        return str(int(y)+1911) + '/' + m  + '/' + d  #民國轉西元
    
def transform_data(data):
    data[0] = datetime.datetime.strptime(transform_date(data[0]), '%Y/%m/%d')
    data[1] = int(data[1].replace(',', ''))  #把千進位的逗點去除
    data[2] = int(data[2].replace(',', ''))
    data[3] = float(data[3].replace(',', ''))
    data[4] = float(data[4].replace(',', ''))
    data[5] = float(data[5].replace(',', ''))
    data[6] = float(data[6].replace(',', ''))
    data[7] = float(0.0 if data[7].replace(',', '') == 'X0.00' else data[7].replace(',', ''))  # +/-/X表示漲/跌/不比價
    data[8] = int(data[8].replace(',', ''))
    return data

def transform(data):
    return [transform_data(d) for d in data]

def getstockdata():
    today=getnewday()
    #return HttpResponse(today)
    try: 
         r = requests.get('https://www.twse.com.tw/fund/T86?response=json&date='+today+'&selectType=ALL')#     
         date_list = []
         database_insert=[]
         data=r.json()['data']
         for x in data:
           if x[0][:1] != '0' and x[0][:2] != '28':
              date_list.append([x[0],x[1]])
         date_list=date_list[:20]
         for i in range(20):
             r = requests.get('https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=%s&stockNo=%s' % ( today, date_list[i][0]))
             time.sleep(1)
             j=r.json()["data"]
             todaydata = r.json()["data"][len(j)-1]#今天
             avg=(float(todaydata[6])+float(todaydata[3]))/2
             Stock = stock(stock_id=date_list[i][0], stock_date=todaydata[0], buy_date=todaydata[0], stock_name=date_list[i][1], open=todaydata[3],
                 high=todaydata[4] ,low=todaydata[5], close=todaydata[6],Increase=todaydata[7],buy=avg)
             database_insert.append(Stock) 
            
         stock.objects.bulk_create(database_insert)   
         return "true"
    except:
         return "flase"



def stock1_view(request):
       today=getnewday()
       #return HttpResponse(getdata)
       today=str(int(today[0:4])-1911 )+"/"+str(today[4:6])+"/"+str(today[6:8])
       today_get=stock.objects.filter(stock_date=today).count()
       if today_get == 0:
           
           getdata=getstockdata()
       try: 
         date_list =  stock.objects.filter(stock_date=today) #漲幅
        
       except:
          errormessage1 = " (讀取錯誤!)"

       return render(request, "stock.html",locals())