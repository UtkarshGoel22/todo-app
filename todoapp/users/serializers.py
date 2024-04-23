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


class UserSerializer(BaseUserSerializer):
    """
    Base serializer for user model.
    """

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('id',)


class UserPendingTodoSerializer(UserSerializer):
    """
    User pending todo serializer.
    """

    pending_count = rest_serializers.IntegerField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('pending_count',)


class UserTodoStatsSerializer(UserPendingTodoSerializer):
    """
    User todo stats serializer.
    """

    completed_count = rest_serializers.IntegerField()

    class Meta(UserPendingTodoSerializer.Meta):
        fields = UserPendingTodoSerializer.Meta.fields + ('completed_count',)


class UserWiseProjectSerializer(BaseUserSerializer):
    """
    User wise project stats serializer.
    """

    to_do_projects = rest_serializers.SerializerMethodField()
    in_progress_projects = rest_serializers.SerializerMethodField()
    completed_projects = rest_serializers.SerializerMethodField()

    def _remove_none_from_list(self, project_names: list) -> list:
        """
        Method to remove None values from a list.

        Args:
            project_names (list): Project names.

        Returns:
            list: Project names whose value is not None.
        """

        return [project_name for project_name in project_names if project_name is not None]

    def get_to_do_projects(self, obj) -> list:
        """
        Method to populate to_do_projects field.

        Args:
            obj (CustomUser): CustomUser model instance.

        Returns:
            list: Project names which are yet to be started.
        """

        return self._remove_none_from_list(obj['to_do_projects'])
    
    def get_in_progress_projects(self, obj) -> list:
        """
        Method to populate in_progress_projects field.

        Args:
            obj (CustomUser): CustomUser model instance.

        Returns:
            list: Project names which are in progress.
        """

        return self._remove_none_from_list(obj['in_progress_projects'])
    
    def get_completed_projects(self, obj) -> list:
        """
        Method to populate completed_projects field.

        Args:
            obj (CustomUser): CustomUser model instance.

        Returns:
            list: Project names which are completed.
        """

        return self._remove_none_from_list(obj['completed_projects'])

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('to_do_projects', 'in_progress_projects', 'completed_projects')
