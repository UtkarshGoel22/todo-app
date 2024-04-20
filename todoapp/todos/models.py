from django.conf import settings
from django.db import models

from commons import constants as common_constants


class Todo(models.Model):
    """
    Fields:
        user (ForeignKey to User model)
        name (Name of the todo. Max length is 150)
        done (Default value is False)
        date_created (Default value is the time of Todo object creation)
        date_completed (Set when done is marked to True)
    """
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=common_constants.NAME_MAX_LENGTH)
    done = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    
    def __str__(self) -> str:
        """
        String representation of the Todo object.

        Returns:
            str: Name of the todo.
        """

        return self.name
