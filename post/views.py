from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post
from .models import About
from .models import Experience
from .models import Education
from .models import Skills
from .models import Projects
from .models import Awards
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
    
    try: 
        edu = Education.objects.all().order_by('-duringstart') #讀取所有學歷。
    except:
        errormessage2 = " (讀取錯誤!)"
    
    try: 
        skill = Skills.objects.all().order_by('id') #讀取所有學歷。
    except:
        errormessage3 = " (讀取錯誤!)"
    try: 
        project = Projects.objects.all().order_by('id') #讀取所有專案。
    except:
        errormessage4 = " (讀取錯誤!)"

    try: 
        award = Awards.objects.all().order_by('id') #讀取所有專案。
    except:
        errormessage5 = " (讀取錯誤!)"
     
        
    return render(request, "post_list.html", locals())

class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'