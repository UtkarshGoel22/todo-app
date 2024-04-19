from collections import OrderedDict

from django.contrib.auth import authenticate, hashers, get_user_model
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


class LoginUserSerializer(rest_serializers.Serializer):
    """
    Login user API serializer.
    """

    email = rest_serializers.EmailField(write_only=True)
    password = rest_serializers.CharField(write_only=True, trim_whitespace=False)
    auth_token = rest_serializers.SerializerMethodField()

    def get_auth_token(self, obj) -> str:
        """
        Method to populate auth_token field.

        Args:
            obj (OrderedDict): Request data.

        Returns:
            str: Auth token
        """

        token, _ = Token.objects.get_or_create(user=self.user)
        return token.key

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        """
        Method to authenticate user.
        If the credentials provided by the user are valid then populate the 'auth_token' field.

        Args:
            attrs (OrderedDict): Request data.

        Raises:
            AuthenticationFailed: When the credentials provided by the user are incorrect.

        Returns:
            OrderedDict: Request data.
        """

        self.user = authenticate(username=attrs['email'], password=attrs['password'])
        if not self.user:
            raise rest_exceptions.AuthenticationFailed({'error': [user_constants.ERROR_MESSAGES['INVALID_CREDENTIALS']]})

        return attrs

    class Meta:
        fields = ('email', 'password', 'auth_token')
