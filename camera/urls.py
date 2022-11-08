from django.urls import path
from . import views
from django .contrib.auth.decorators import login_required
urlpatterns = [

    path('add/', login_required(views.job_add_task)),
    path('del/', login_required(views.job_del_task)),
    path('pause/', login_required(views.job_pause_task)),
    path('resume/', login_required(views.job_resume_task)),
    path('runonce/', login_required(views.job_run_once)),
    path('list', login_required(views.job_list_task)),
 ]