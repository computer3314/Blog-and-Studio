# Generated by Django 4.1.2 on 2022-10-24 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0007_camera_fps_camera_heigth_camera_width'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='cameraDisplay',
            field=models.BooleanField(default=True, verbose_name='是否啟動相機'),
        ),
    ]
