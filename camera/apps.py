from django.apps import AppConfig
import time

from Demo.templatetags import custom_tags

class CameraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'camera'
    def ready(self):
            custom_tags.version = int(round(time.time() * 1000))