from rest_framework import (
    exceptions as rest_exceptions,
    generics as rest_generics,
    permissions as rest_permissions,
    response as rest_response,
)

from users import serializers as user_serializers


class UserRegistrationAPIView(rest_generics.CreateAPIView):
    """
    User registration view
    """

    serializer_class = user_serializers.RegisterUserSerializer
    authentication_classes = ()
    permission_classes = (rest_permissions.AllowAny,)


class UserLoginAPIView(rest_generics.GenericAPIView):
    """
    User login view
    """

    serializer_class = user_serializers.LoginUserSerializer
    authentication_classes = ()
    permission_classes = (rest_permissions.AllowAny,)

    def post(self, request, *args, **kwargs) -> rest_response.Response:
        """
        Post method for logging in the user.

        Args:
            request: Request object

        Returns:
            Response: Response containing authentication token.
        """
        
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except rest_exceptions.AuthenticationFailed as error:
            return rest_response.Response(error.detail, error.status_code)

        return rest_response.Response(serializer.data)
