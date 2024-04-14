from django.conf import settings
from django.db import models

from commons import constants as common_constants


class Project(models.Model):
    """
    Feilds:
        members (Many To Many field to User model. Created using a through table)
        name (Max length is 150)
        max_members (Positive integer)
        status (Choice field integer type: 0(To be started) / 1(In progress) / 2(Completed). Default value is 0)
    """
    
    TO_BE_STARTED = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    STATUS_CHOICES = (
        (TO_BE_STARTED, 'To be started'),
        (IN_PROGRESS, 'In progress'),
        (COMPLETED, 'Completed'),
    )
    
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ProjectMember')
    name = models.CharField(max_length=common_constants.NAME_MAX_LENGTH)
    max_members = models.PositiveIntegerField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=TO_BE_STARTED)

    def __str__(self) -> str:
        """
        String representation of the Project object.

        Returns:
            str: Name of the project.
        """

        return self.name


class ProjectMember(models.Model):
    """
    Fields:
        project (ForeignKey to Project model)
        member (ForeignKey to User model)
        project and member are unique together.
    """
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('member', 'project')
    
    def __str__(self) -> str:
        """
        String representation of ProjectMember object.

        Returns:
            str: Project name - member email.
        """
        
        return f'{self.project.name}-{self.member.email}'
