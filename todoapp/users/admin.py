from django.contrib import admin
from django.contrib.auth import get_user_model


class UserAdmin(admin.ModelAdmin):

    list_display = ('first_name', 'last_name', 'email', 'date_joined', 'is_staff', 'is_superuser', 'last_login')


admin.site.register(get_user_model(), UserAdmin)
