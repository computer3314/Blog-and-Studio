from django.contrib import admin
from .models import Camera
from .models import Move
# Register your models here.
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id','camera_id','camera_url', 'title','width')
    search_fields = ('id','camera_id','camera_url','title')
class MoveAdmin(admin.ModelAdmin):
    list_display = ('id','camera_id','movetime', 'photo')
    search_fields = ('id','camera_id','movetime','photo')

admin.site.register(Camera, CameraAdmin)
admin.site.register(Move, MoveAdmin)