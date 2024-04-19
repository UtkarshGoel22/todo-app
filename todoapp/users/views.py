from rest_framework import (
    generics as rest_generics,
    permissions as rest_permissions,
)

from users import serializers as user_serializers


class UserRegistrationAPIView(rest_generics.CreateAPIView):
    """
    User registration view
    """

    serializer_class = user_serializers.RegisterUserSerializer
    authentication_classes = ()
    permission_classes = (rest_permissions.AllowAny,)
