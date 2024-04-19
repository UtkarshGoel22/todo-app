from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import (
    exceptions as rest_exceptions,
    serializers as rest_serializers,
)

from projects import (
    constants as project_constants,
    models as project_models,
)


class ProjectMemberSerializer(rest_serializers.Serializer):
    """
    Project Member Api Serializer.
    """

    user_ids = rest_serializers.ListField(
        child=rest_serializers.IntegerField(),
        write_only=True,
        min_length=project_constants.MIN_LENGTH,
        max_length=project_constants.MAX_LENGTH,
    )

    def validate_user_ids(self, user_ids: list) -> list:
        """
        Field level validation for 'user_ids'.
        Remove duplicate ids present in the field.  

        Args:
            user_ids (list): User ids.

        Returns:
            list: User ids.
        """

        return list(set(user_ids))

    def get_user_wise_project_count_and_valid_user_ids(self) -> tuple:
        """
        Method to get user wise project count and user ids of valid users.

        Returns:
            tuple: dict containing user wise project count, set containing ids of valid users.
        """

        user_wise_project_count = dict(
            get_user_model().objects
            .filter(id__in=self.validated_data['user_ids'])
            .annotate(project_count=Count('project'))
            .prefetch_related('project_set')
            .values_list('id', 'project_count')
        )

        return user_wise_project_count, set(user_wise_project_count.keys())

    def check_for_invalid_user_ids(self, valid_user_ids: set) -> None:
        """
        Method to check for invalid user ids.

        Args:
            valid_user_ids (set): Valid user ids.

        Raises:
            ValidationError: When any of the user id in the request data is invalid.
        """

        # Invalid user ids present in request data.
        if set(self.validated_data['user_ids']).difference(valid_user_ids):
            raise rest_exceptions.ValidationError({'user_ids': [project_constants.ERROR_MESSAGES['INVALID_USER_IDS']]})

    def add_members(self, project: dict) -> dict:
        """
        Method to add members in a project.

        Args:
            project (dict): Project data.

        Returns:
            dict: Containing logs for each user_id.
        """

        logs = {}
        users_to_be_added = []
        project_max_limit_reached = False
        user_wise_project_count, valid_user_ids = self.get_user_wise_project_count_and_valid_user_ids()

        self.check_for_invalid_user_ids(valid_user_ids)

        for user_id in valid_user_ids:
            # User is already a member of the project.
            if user_id in project['users']:
                logs[user_id] = project_constants.ERROR_MESSAGES['ALREADY_MEMBER_OF_PROJECT']
            # User is already part of 2 projects.
            elif user_wise_project_count[user_id] >= project_constants.MAX_ASSOCIATED_PROJECTS:
                logs[user_id] = project_constants.ERROR_MESSAGES['MAX_ASSOCIATED_PROJECTS_LIMIT']
            # User can be added in the project if max limit is not reached.
            else:
                users_to_be_added.append(project_models.ProjectMember(project_id=project['id'], member_id=user_id))
                logs[user_id] = project_constants.SUCCESS_MESSAGES['MEMBER_ADDED_SUCCESSFULLY']

        # Maximum member limit reached for the project
        if project["existing_members"] + len(users_to_be_added) > project["max_members"]:
            project_max_limit_reached = True
            message = project_constants.ERROR_MESSAGES["PROJECT_MEMBERS_MAX_LIMIT_REACHED"].format(
                remaining_members=project_constants.NO_SPACE_LEFT
                if project["existing_members"] >= project["max_members"]
                else project["max_members"] - project["existing_members"]
            )
            for project_member in users_to_be_added:
                logs[project_member.member_id] = message

        if not project_max_limit_reached and users_to_be_added:
            project_models.ProjectMember.objects.bulk_create(users_to_be_added)

        return {'logs': logs}

    def remove_members(self, project: dict) -> dict:
        """
        Method to remove members from a project.

        Args:
            project (dict): Project data.

        Returns:
            dict: Containing logs for each user_id.
        """

        logs = {}
        _, valid_user_ids = self.get_user_wise_project_count_and_valid_user_ids()
        users_to_remove = []

        self.check_for_invalid_user_ids(valid_user_ids)

        for user_id in valid_user_ids:
            # User is a member of the project.
            if user_id in project['users']:
                logs[user_id] = project_constants.SUCCESS_MESSAGES['MEMBER_REMOVED_SUCCESSFULLY']
                users_to_remove.append(user_id)
            else:
                logs[user_id] = project_constants.ERROR_MESSAGES['NOT_A_MEMBER_OF_PROJECT']

        if users_to_remove:
            project_models.ProjectMember.objects.filter(project_id=project['id'], member_id__in=users_to_remove).delete()

        return {'logs': logs}

    class Meta:
        fields = ('user_ids',)
