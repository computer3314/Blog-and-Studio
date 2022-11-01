from django.contrib import admin
from .models import Camera
from .models import Move
from camera.cameras import CameraFactory, BaseCamera
import threading
# Register your models here.
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id','camera_id','camera_url', 'title','width')
    search_fields = ('id','camera_id','camera_url','title')
    def save_model(self, request, obj, form, change):
        thread=threading.Thread(target= CameraFactory.update_camera,args=(obj,))#舊檔案備份更換檔案
        thread.daemon = True
        thread.start()
        super().save_model(request, obj, form, change)
    def delete_queryset(self, request, queryset):
        print('==========================delete_queryset==========================')
        print(queryset)

        """
        you can do anything here BEFORE deleting the object(s)
        """

        queryset.delete()

        """
        you can do anything here AFTER deleting the object(s)
        """

        print('==========================delete_queryset==========================')
class MoveAdmin(admin.ModelAdmin):
    list_display = ('id','camera_id','movetime', 'photo')
    search_fields = ('id','camera_id','movetime','photo')

admin.site.register(Camera, CameraAdmin)
admin.site.register(Move, MoveAdmin)