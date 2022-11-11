from django.contrib import admin
from .models import Chat
# Register your models here.
class ChatAdmin(admin.ModelAdmin):
    list_display = ('roomname','nickname','message', 'created_at')
    search_fields = ('roomname','nickname','message', 'created_at')

admin.site.register(Chat, ChatAdmin)