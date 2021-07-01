from django.contrib import admin
from .models import Post
from .models import About
from .models import Experience

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content')
    search_fields = ('title', 'content')
class AboutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'introduction', 'photo', 'mail', 'phone', 'address', 'twitterid', 'fbid', 'igid', 'githubid')
    search_fields = ('introduction', 'photo', 'mail', 'phone', 'address', 'twitterid', 'fbid', 'igid', 'githubid')


# Register your models here.
class PostExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'companyname', 'position', 'content', 'start', 'end')
    search_fields = ('companyname', 'position', 'content', 'start', 'end')



admin.site.register(About, AboutAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Experience, PostExperienceAdmin)
