from rest_framework import routers

from todos import views as todo_views

app_name = 'todos'

router = routers.SimpleRouter()
router.register('', todo_views.TodoAPIViewSet, 'todos')

urlpatterns = router.urls
