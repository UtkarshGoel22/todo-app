from collections import OrderedDict

from django.contrib.auth import hashers, get_user_model
from rest_framework import (
    serializers as rest_serializers,
    exceptions as rest_exceptions,
)
from rest_framework.authtoken.models import Token

from users import constants as user_constants


class BaseUserSerializer(rest_serializers.ModelSerializer):
    """
    Base serializer for User model.
    """

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')


class RegisterUserSerializer(BaseUserSerializer):
    """
    Register user API serializer.
    """

    confirm_password = rest_serializers.CharField(write_only=True, trim_whitespace=False)
    token = rest_serializers.SerializerMethodField()

    def get_token(self, obj) -> str:
        """
        Method to populate token field.

        Args:
            obj (CustomUser): CustomUser model instance.

        Returns:
            str: User token.
        """

        return Token.objects.create(user=obj).key

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        """
        Method to validate request data.
        Checks whether 'password' and 'confirm_password' are equal or not.

        Args:
            attrs (OrderedDict): Request data.

        Raises:
            ValidationError: When 'password' and 'confirm_password' are not equal.

        Returns:
            OrderedDict: Request data.
        """
    
        if attrs['password'] != attrs['confirm_password']:
            raise rest_exceptions.ValidationError({'password': [user_constants.ERROR_MESSAGES['PASSWORD_MISMATCH']]})
        attrs.update({'password': hashers.make_password(attrs['password'])})
        attrs.pop('confirm_password')

        return attrs

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('date_joined', 'password', 'confirm_password', 'token')
        extra_kwargs = {'password': {'write_only': True, 'trim_whitespace': False}}
