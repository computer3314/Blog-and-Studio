from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post
from .models import About
from .models import Experience
# Create your views here.


def aboutget(request): 
    try: 
        unit = About.objects.get(id="1") #讀取第一筆個人資料
    except:
        errormessage = " (讀取錯誤!)"

    try: 
        exp = Experience.objects.all().order_by('-start') #讀取所有經驗。
    except:
        errormessage1 = " (讀取錯誤!)"
    return render(request, "post_list.html", locals())

class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'