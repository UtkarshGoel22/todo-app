from rest_framework import routers

from projects import views as project_views

app_name = 'projects'

router = routers.SimpleRouter()
router.register('', project_views.ProjectMemberApiViewSet, 'projects')

urlpatterns = router.urls
