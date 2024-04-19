from django.urls import re_path

from users import views as user_views

app_name = 'users'

urlpatterns = [
    re_path(r'', user_views.UserRegistrationAPIView.as_view(), name='register'),
]
