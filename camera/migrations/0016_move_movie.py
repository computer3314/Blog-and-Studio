# Generated by Django 3.2.16 on 2022-10-31 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0015_auto_20221029_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='move',
            name='movie',
            field=models.URLField(blank=True, null=True, verbose_name='查看錄影'),
        ),
    ]
