from django.contrib import admin

from todos import models as todo_models


class TodoAdmin(admin.ModelAdmin):

    list_display = ('user', 'name', 'done', 'date_created')
    list_filter = ('done', 'date_created')


admin.site.register(todo_models.Todo, TodoAdmin)
