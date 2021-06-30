from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import About

# Create your views here.

def aboutget(request): 
    try: 
        unit = About.objects.get(id="1") #讀取一筆資料
    except:
        errormessage = " (讀取錯誤!)"
    return render(request, "post_list.html", locals())