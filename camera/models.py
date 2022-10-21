import queue
import threading

import cv2
from django.db import models

class Camera(models.Model):
    """A typical class defining a model, derived from the Model class."""
    # Metadata
    class Meta:
        verbose_name = '攝影機'
        verbose_name_plural = '攝影機'
    camera_id = models.TextField('網路攝影機', max_length=100,default='0')
    title = models.CharField('標題', max_length=20,default='test')
    # Methods
    def camera_api(self):
        """Returns the URL to access a particular instance of MyModelName."""
        return int(self.camera_id)

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.title
