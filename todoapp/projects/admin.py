from django.contrib import admin

from projects import models as project_models


class ProjectAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'name', 'max_members', 'status')
    list_filter = ('members',)
    

class ProjectMemberAdmin(admin.ModelAdmin):
    
    list_display = ('project', 'member')


admin.site.register(project_models.Project, ProjectAdmin)
admin.site.register(project_models.ProjectMember, ProjectMemberAdmin)
