from django.contrib import admin
from .models import Camera,File
from .models import Move
from camera.cameras import CameraFactory, BaseCamera
import threading

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
# Register your models here.
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id','camera_id','camera_url', 'title','width')
    search_fields = ('id','camera_id','camera_url','title','width')
    def save_model(self, request, obj, form, change):
        thread=threading.Thread(target= CameraFactory.update_camera,args=(obj,))#舊檔案備份更換檔案
        thread.daemon = True
        thread.start()
        super().save_model(request, obj, form, change)
    def delete_queryset(self, request, queryset):
        logger.info('==========================delete_queryset==========================')
        logger.info(queryset)

        """
        you can do anything here BEFORE deleting the object(s)
        """

        queryset.delete()

        """
        you can do anything here AFTER deleting the object(s)
        """

        logger.info('==========================delete_queryset==========================')
class MoveAdmin(admin.ModelAdmin):
    list_display = ('id','camera','movetime', 'photo','movie')
    search_fields = ('id','camera','movetime','photo','movie')
class FileAdmin(admin.ModelAdmin):
    list_display = ('camera','starttime','endtime', 'movie','created_at')
    search_fields = ('camera','starttime','endtime', 'movie','created_at')
admin.site.register(Camera, CameraAdmin)
admin.site.register(Move, MoveAdmin)
admin.site.register(File, FileAdmin)