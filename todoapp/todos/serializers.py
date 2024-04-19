from collections import OrderedDict

from django.utils import timezone
from rest_framework import serializers

from todos import (
    constants as todo_constants,
    models as todo_models
)


class BaseTodoSerializer(serializers.ModelSerializer):
    """
    Base Todo API Serializer.
    """

    class Meta:
        model = todo_models.Todo
        fields = ('name', 'done', 'date_created')
        extra_kwargs = {'name': {'read_only': True}}
        

class CreateTodoSerializer(BaseTodoSerializer):
    """
    Create Todo API Serializer.
    """

    todo = serializers.CharField(max_length=todo_constants.NAME_MAX_LENGTH, write_only=True, source='name')

    class Meta(BaseTodoSerializer.Meta):
        fields = BaseTodoSerializer.Meta.fields + ('todo',)
        extra_kwargs = {**BaseTodoSerializer.Meta.extra_kwargs, 'done': {'read_only': True}}


class UpdateTodoSerializer(BaseTodoSerializer):
    """
    Update Todo API Serializer.
    """

    done = serializers.BooleanField()
    todo = serializers.CharField(max_length=todo_constants.NAME_MAX_LENGTH, write_only=True, source='name')
    
    def validate(self, attrs: OrderedDict) -> dict:
        """
        Method to validate request data.
        Update 'date_created' field based on the value 'done' field i.e.
        set date_created to current date time if done = True.

        Args:
            attrs (OrderedDict): Request data.

        Returns:
            OrderedDict: Request data.
        """

        if attrs.get('done') is True:
            attrs['date_completed'] = timezone.now()
        elif attrs.get('done') is False:
            attrs['date_completed'] = None
        return attrs

    class Meta(BaseTodoSerializer.Meta):
        fields = BaseTodoSerializer.Meta.fields + ('todo', 'date_completed')
        extra_kwargs = {**BaseTodoSerializer.Meta.extra_kwargs, 'date_completed': {'write_only': True}}
