from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Count
from rest_framework import (
    decorators as rest_decorators,
    response as rest_response,
    viewsets as rest_viewsets,
)

from projects import (
    models as project_models,
    serializers as project_serializers,
)


class ProjectMemberApiViewSet(rest_viewsets.GenericViewSet):
    """
    Project member API viewset for adding and removing members from a project.
    
    Constraints:
        - A user can be a member of max 2 projects only.
        - A project can have at max N members defined in database for each project.

    Cases:
        - User gets added successfully.
        - User is already a member of the project.
        - User is already part of 2 projects.
        - Invalid user ids.
        - Invalid project ids.
        - Max limit reached of project members.
        - Duplicate user ids in request data.
        - Only a project member can add/remove a member.
        - User is not part of the project during removal.
        - Limit number of user ids in request data.
    """

    serializer_class = project_serializers.ProjectMemberSerializer
    lookup_url_kwarg = 'project_id'

    def get_queryset(self):
        """
        Method to get the queryset for the view set.
        """

        return (
            project_models.Project.objects
            .annotate(existing_members=Count('projectmember__id'))
            .annotate(users=ArrayAgg('projectmember__member__id'))
            .filter(projectmember__member__id=self.request.user.id)
            .values('id', 'existing_members', 'max_members', 'users')
        )

    @rest_decorators.action(methods=['patch'], detail=True, url_path='add-members', url_name='add-members')
    def add_members_to_project(self, request, *args, **kwargs) -> rest_response.Response:
        """
        Method for adding members to a project.

        Args:
            request: Request data.

        Returns:
            Response: Response containing information for each user id provided in request data.
        """

        project = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logs = serializer.add_members(project)

        return rest_response.Response(logs)

    @rest_decorators.action(methods=['patch'], detail=True, url_path='remove-members', url_name='remove-members')
    def remove_members_from_project(self, request, *args, **kwargs) -> rest_response.Response:
        """
        Method to remove members from a project.

        Args:
            request: Request data.

        Returns:
            Response: Response containing information for each user id provided in request data.
        """

        project = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        logs = serializer.remove_members(project)

        return rest_response.Response(logs)
