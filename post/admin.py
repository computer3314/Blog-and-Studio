from django.contrib import admin
from .models import Post
from .models import About
from .models import Experience
from .models import Education
from .models import Skills
from .models import Projects
from .models import Awards
# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content')
    search_fields = ('title', 'content')
class AboutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'introduction', 'photo', 'mail', 'phone', 'address', 'twitterid', 'fbid', 'igid', 'githubid','interests')
    search_fields = ('introduction', 'photo', 'mail', 'phone', 'address', 'twitterid', 'fbid', 'igid', 'githubid')


# Register your models here.
class PostExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'companyname', 'position', 'content', 'start', 'end')
    search_fields = ('companyname', 'position', 'content', 'start', 'end')

class EducationAdmin(admin.ModelAdmin):
    list_display = ('id', 'school', 'department', 'status', 'duringstart', 'duringsend')
    search_fields = ('school', 'department', 'status', 'duringstart', 'duringsend')

class SkillsAdmin(admin.ModelAdmin):
    list_display = ('id', 'skillname', 'skillcontect', 'skilltag')
    search_fields = ('skillname', 'skillcontect', 'skilltag')

class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('id', 'projectname', 'projectstart', 'projectend', 'projectcontent', 'projecturl','projectimg')
    search_fields = ('projectname', 'projectstart', 'projectend', 'projectcontent', 'projecturl','projectimg')

class AwardsAdmin(admin.ModelAdmin):
    list_display = ('id', 'awardname', 'awarddate')
    search_fields = ('awardname', 'awarddate')

admin.site.register(Awards, AwardsAdmin)
admin.site.register(Projects, ProjectsAdmin)
admin.site.register(Skills, SkillsAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(About, AboutAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Experience, PostExperienceAdmin)
