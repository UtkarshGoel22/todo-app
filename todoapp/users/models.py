from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from commons import constants as common_constants


class UserManager(BaseUserManager):
    
    def create_user(self, email: str, password: str, **other_fields):
        """
        Function to create user in database.

        Args:
            email (str): Email address of the user. 
            password (str): Password of the user.

        Raises:
            ValueError: When any one of the first name, email or password is None.
        """

        if not (email and password): 
            raise ValueError('Both email and password must be set.')
        
        email = self.normalize_email(email)

        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()

        return user
    
    def create_superuser(self, email: str, password: str, **other_fields):
        """
        Function to create superuser in database.

        Args:
            email (str): Email address of the user. 
            password (str): Password of the user.

        Raises:
            ValueError: When is_staff or is_superuser is False. 
        """
        
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **other_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Fields:
        first_name (Max length is 150)
        last_name (Max length is 150)
        email (Unique)
        password (Inherited from AbstractBaseUser. Password is encrypted before saving.)
        date_joined (Default value is the time of User object creation)
        last_login (Inherited from AbstractBaseUser)
        is_staff (Default value should be False)
        is_superuser (Inherited from PermissionsMixin)
    """
    
    first_name = models.CharField(max_length=common_constants.NAME_MAX_LENGTH, blank=True)
    last_name = models.CharField(max_length=common_constants.NAME_MAX_LENGTH, blank=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def get_short_name(self) -> str:
        """
        Function to get short name of the user.

        Returns:
            str: The first name of the user.
        """

        return self.first_name
    
    def get_full_name(self) -> str:
        """
        Function to get the full name of the user.

        Returns:
            str: The full name of the user i.e. first_name + last_name.
        """
        
        return f'{self.first_name} {self.last_name}'.strip()
