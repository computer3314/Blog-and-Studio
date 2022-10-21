from django.contrib import admin
from .models import Camera
# Register your models here.
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'title','camera_id')
    search_fields = ('id','title','camera_id')

admin.site.register(Camera, CameraAdmin)