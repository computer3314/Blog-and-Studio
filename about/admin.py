from django.contrib import admin
from .models import About

# Register your models here.
class AboutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'introduction', 'photo', 'mail', 'phone', 'address', 'twitterid', 'fbid', 'igid', 'githubid')
    search_fields = ('introduction', 'photo', 'mail', 'phone', 'address', 'twitterid', 'fbid', 'igid', 'githubid')

admin.site.register(About, AboutAdmin)
