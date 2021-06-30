from django.contrib import admin
from .models import Experience
# Register your models here.
class PostExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'companyname', 'position', 'content', 'start', 'end')
    search_fields = ('companyname', 'position', 'content', 'start', 'end')

admin.site.register(Experience, PostExperienceAdmin)