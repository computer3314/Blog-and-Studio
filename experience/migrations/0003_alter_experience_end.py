# Generated by Django 3.2.4 on 2021-06-30 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experience', '0002_alter_experience_end'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='end',
            field=models.DateField(blank=True, null=True, verbose_name='工作時間迄'),
        ),
    ]
