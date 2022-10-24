from django.contrib import admin
from .models import Camera
# Register your models here.
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id','camera_id','camera_url', 'title','width')
    search_fields = ('id','camera_id','camera_url','title')

admin.site.register(Camera, CameraAdmin)