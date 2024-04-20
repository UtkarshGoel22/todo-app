from rest_framework.viewsets import ModelViewSet

from commons import (
    mixins as common_mixins,
    pagination as common_pagination,
)
from todos import (
    models as todo_models,
    serializers as todo_serializers,
)


class TodoAPIViewSet(common_mixins.SerializerToActionMapperMixin, ModelViewSet):
    """
    Todo API viewset
    """

    pagination_class = common_pagination.CustomPagination
    serializer_classes = {
        'create': todo_serializers.CreateTodoSerializer,
        'list': todo_serializers.UpdateTodoSerializer,
        'retrieve': todo_serializers.UpdateTodoSerializer,
        'update': todo_serializers.UpdateTodoSerializer,
        'partial_update': todo_serializers.UpdateTodoSerializer,
    }
    lookup_url_kwarg = 'todo_id'

    def perform_create(self, serializer) -> None:
        """
        Method to save todo during new todo creation.

        Args:
            serializer (CreateTodoAPISerializer): Create todo API serializer.
        """

        serializer.save(user_id=self.request.user.id)

    def get_queryset(self):
        """
        Method to get the queryset for the view set.
        """

        return todo_models.Todo.objects.filter(user_id=self.request.user.id)
