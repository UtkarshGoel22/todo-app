import json

from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Case, CharField, Count, IntegerField, Prefetch, Sum, Q, When

from projects import (
    models as project_models,
    serializers as project_serializers,
)
from todos import (
    models as todo_models,
    serializers as todo_serializers,
)
from users import serializers as user_serializers


def fetch_all_users() -> list[dict]:
    """
    Util to fetch all the users.

    Returns:
        list[dict]: Contains user's id, first_name, last_name and email in each element.
            [
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@example.com",
                },
            ]
    """
    
    # SQL Query:
    # SELECT id, first_name, last_name, email FROM users_customuser;
    
    # SQL Query used by Posgtres:
    # SELECT "users_customuser"."id", "users_customuser"."first_name", "users_customuser"."last_name", "users_customuser"."email" FROM "users_customuser"
    
    users_qs = get_user_model().objects.values('id', 'first_name', 'last_name', 'email')
    
    return json.loads(json.dumps(user_serializers.UserSerializer(users_qs, many=True).data))


def fetch_all_todo_list_with_user_details() -> list[dict]:
    """
    Util to fetch all todos along with user details.
    Status is "Done" when done=True else "To do".

    Returns:
        list[dict]: Contains todo's id, name, status, created_at and creator.
            [
                {
                    "id": 1,
                    "name": "Buy groceries",
                    "status": "Done",
                    "created_at": "4:30 PM, 12 Dec, 2021"
                    "creator" : {
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john@email.com",
                },
            ]
    """
    
    # SQL Query:
    # SELECT
    #   todo.id, todo.user_id, todo.name, todo.done, todo.date_created,
    #   user.id, user.first_name, user.last_name, user.email
    # FROM todos_todo AS todo
    # INNER JOIN users_customuser AS user ON (todo.user_id = user.id);
    
    # SQL Query used by Postgres:
    # SELECT
    #   "todos_todo"."id", "todos_todo"."user_id", "todos_todo"."name", "todos_todo"."done", "todos_todo"."date_created",
    #   "users_customuser"."id", "users_customuser"."first_name", "users_customuser"."last_name", "users_customuser"."email"
    # FROM "todos_todo"
    # INNER JOIN "users_customuser" ON ("todos_todo"."user_id" = "users_customuser"."id")
    
    todos_qs = (
        todo_models.Todo.objects
        .select_related('user')
        .only('id', 'name', 'done', 'date_created', 'user__first_name', 'user__last_name', 'user__email')
    )
    
    return json.loads(json.dumps(todo_serializers.TodoSerializer(todos_qs, many=True).data))


def fetch_projects_details() -> list[dict]:
    """
    Util to fetch all projects.

    Returns:
        list[dict]: Contains project's id, name, status, existing_member_count and max_members.
            [
                {
                    "id": 1,
                    "name": "Project A",
                    "status": "To Do",
                    "existing_member_count": 2,
                    "max_members": 4,
                },
            ]
    """
    
    # SQL Query used by Postgres:
    # SELECT
    #   "projects_project"."id",
    #   "projects_project"."name",
    #   "projects_project"."max_members",
    #   "projects_project"."status",
    #   COUNT("projects_projectmember"."id") AS "existing_member_count"
    # FROM "projects_project"
    # LEFT OUTER JOIN "projects_projectmember" ON ("projects_project"."id" = "projects_projectmember"."project_id") GROUP BY "projects_project"."id"
    
    projects_qs = (
        project_models.Project.objects
        .annotate(existing_member_count=Count('projectmember__id'))
        .only('id', 'name', 'status', 'max_members')
    )
    
    return json.loads(json.dumps(project_serializers.ProjectSerializer(projects_qs, many=True).data))


def fetch_users_todo_stats() -> list[dict]:
    """
    Util to fetch todos list stats of all users on platform.

    Returns:
        list[dict]: Contains user's id, first_name, last_name, email, count of completed and pending todos.
            [
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@email.com",
                    "completed_count": 1,
                    "pending_count": 2,
                },
            ]
    """
    
    # SQL Query used by Postgres:
    # SELECT
    #   "users_customuser"."id",
    #   "users_customuser"."first_name",
    #   "users_customuser"."last_name",
    #   "users_customuser"."email",
    #   COUNT(CASE WHEN "todos_todo"."done" THEN 1 ELSE NULL END) AS "completed_count",
    #   COUNT(CASE WHEN NOT "todos_todo"."done" THEN 1 ELSE NULL END) AS "pending_count"
    # FROM "users_customuser"
    # LEFT OUTER JOIN "todos_todo" ON ("users_customuser"."id" = "todos_todo"."user_id")
    # GROUP BY "users_customuser"."id"
    
    users_qs = (
        get_user_model().objects
        .annotate(
            completed_count=Count(Case(When(todo__done=True, then=1), output_field=IntegerField())),
            pending_count=Count(Case(When(todo__done=False, then=1), output_field=IntegerField()))
        )
        .values('id', 'first_name', 'last_name', 'email', 'completed_count', 'pending_count')
    )
    
    return json.loads(json.dumps(user_serializers.UserTodoStatsSerializer(users_qs, many=True).data))


def fetch_five_users_with_max_pending_todos() -> list[dict]:
    """
    Util to fetch top five user with maximum number of pending todos.

    Returns:
        list[dict]: Contains user's id, first_name, last_name, email, count of pending todos.
            [
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@email.com",
                    "completed_count": 1,
                    "pending_count": 2,
                },
            ]
    """
    
    # SQL Query used by Postgres:
    # SELECT
    #   "users_customuser"."id",
    #   "users_customuser"."first_name",
    #   "users_customuser"."last_name",
    #   "users_customuser"."email",
    #   COUNT(CASE WHEN NOT "todos_todo"."done" THEN 1 ELSE NULL END) AS "pending_count"
    # FROM "users_customuser"
    # LEFT OUTER JOIN "todos_todo" ON ("users_customuser"."id" = "todos_todo"."user_id")
    # GROUP BY "users_customuser"."id" ORDER BY 5 DESC LIMIT 5
    
    users_qs = (
        get_user_model().objects
        .annotate(pending_count=Count(Case(When(todo__done=False, then=1), output_field=IntegerField())))
        .values('id', 'first_name', 'last_name', 'email', 'pending_count')
        .order_by('-pending_count')[:5]
    )

    return json.loads(json.dumps(user_serializers.UserPendingTodoSerializer(users_qs, many=True).data))


def fetch_users_with_n_pending_todos(n: int) -> list[dict]:
    """
    Util to fetch top five user with maximum number of pending todos

    Args:
        n (int): Count of pending todos

    Returns:
        list[dict]: Contains user's id, first_name, last_name, email, count of pending todos.
            [
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@email.com",
                    "completed_count": 1,
                    "pending_count": 2,
                },
            ]
    """

    # SQL Query used by Postgres:
    # SELECT
    #   "users_customuser"."id",
    #   "users_customuser"."first_name",
    #   "users_customuser"."last_name",
    #   "users_customuser"."email",
    #   SUM(CASE WHEN NOT "todos_todo"."done" THEN 1 ELSE NULL END) AS "pending_count"
    # FROM "users_customuser"
    # LEFT OUTER JOIN "todos_todo" ON ("users_customuser"."id" = "todos_todo"."user_id")
    # GROUP BY "users_customuser"."id"
    # HAVING SUM(CASE WHEN (NOT "todos_todo"."done") THEN 1 ELSE NULL END) = 13

    users_qs = (
        get_user_model().objects
        .annotate(pending_count=Sum(Case(When(todo__done=False, then=1), output_field=IntegerField())))
        .values('id', 'first_name', 'last_name', 'email', 'pending_count')
        .filter(pending_count=n)
    )

    return json.loads(json.dumps(user_serializers.UserPendingTodoSerializer(users_qs, many=True).data))   


def fetch_project_with_member_name_start_or_end_with_u() -> list[dict]:
    """
    Util to fetch project details having members who have name either starting with U or ending with U.

    Returns:
        list[dict]: List of project data
            [
                {
                    "project_name": "Project A",
                    "done": False,
                    "max_members": 3,
                },
            ]
    """
    
    # SQL Query used by Postgres:
    # SELECT DISTINCT 
    #   "projects_project"."name",
    #   "projects_project"."status",
    #   "projects_project"."max_members"
    # FROM "projects_project"
    # INNER JOIN "projects_projectmember" ON ("projects_project"."id" = "projects_projectmember"."project_id")
    # INNER JOIN "users_customuser" ON ("projects_projectmember"."member_id" = "users_customuser"."id")
    # WHERE (UPPER("users_customuser"."first_name"::text) LIKE UPPER(U%) OR UPPER("users_customuser"."last_name"::text) LIKE UPPER(%U))

    projects_qs = (
        project_models.Project.objects
        .filter(Q(members__first_name__istartswith='U')|Q(members__last_name__iendswith='U'))
        .values('name', 'status', 'max_members')
        .distinct()
    )

    return json.loads(json.dumps(project_serializers.ProjectDetailSerializer(projects_qs, many=True).data))


def fetch_project_wise_report() -> list[dict]:
    """
    Util to fetch project wise todos pending & count per user.    

    Returns:
        list[dict]: List of report data.
            [
                {
                    "project_title": "Project A"
                    "report": [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "email": "john@email.com",
                            "pending_count": 0,
                            "completed_count": 5,
                        }
                        {
                            "first_name": "Utkarsh",
                            "last_name": "Goel",
                            "email": "utkarsh@email.com",
                            "pending_count": 1,
                            "completed_count": 1,
                        },
                    ]
                },
            ]
    """
    
    # SQL Queries used by Postgres
    #
    # SELECT
    #   "users_customuser"."id",
    #   "users_customuser"."password",
    #   "users_customuser"."last_login",
    #   "users_customuser"."is_superuser",
    #   "users_customuser"."first_name",
    #   "users_customuser"."last_name",
    #   "users_customuser"."email",
    #   "users_customuser"."date_joined",
    #   "users_customuser"."is_staff",
    #   SUM(CASE WHEN "todos_todo"."done" THEN 1 ELSE NULL END) AS "completed_count",
    #   SUM(CASE WHEN NOT "todos_todo"."done" THEN 1 ELSE NULL END) AS "pending_count"
    # FROM "users_customuser"
    # LEFT OUTER JOIN "todos_todo" ON ("users_customuser"."id" = "todos_todo"."user_id")
    # GROUP BY "users_customuser"."id"
    # ORDER BY "users_customuser"."first_name" ASC
    #
    # SELECT
    #   "projects_project"."id", "projects_project"."name", "projects_project"."max_members", "projects_project"."status"
    # FROM "projects_project"

    users_qs = (
        get_user_model().objects
        .annotate(
            completed_count=Sum(Case(When(todo__done=True, then=1), output_field=IntegerField())),
            pending_count=Sum(Case(When(todo__done=False, then=1), output_field=IntegerField()))
        )
        .order_by('first_name')
    )

    projects_qs = (
        project_models.Project.objects.prefetch_related(Prefetch('members', to_attr='report', queryset=users_qs))
    )

    return json.loads(json.dumps(project_serializers.ProjectWiseReportSerializer(projects_qs, many=True).data))

def fetch_user_wise_project_status() -> list[dict]:
    """
    Util to fetch user wise project statuses.

    Returns:
        list[dict]: List of user project data.
            [
                {
                    "first_name": "Josh",
                    "last_name": "Doe",
                    "email": "john@email.com",
                    "to_do_projects": ["Project A", "Project B"],
                    "in_progress_projects": ["Project C", "Project D"],
                    "completed_projects": ["Project E", "Project F"],
                },
            ]
    """
    
    # SELECT
    #   "users_customuser"."first_name",
    #   "users_customuser"."last_name",
    #   "users_customuser"."email",
    #   ARRAY_AGG(CASE WHEN "projects_project"."status" = 0 THEN "projects_project"."name" ELSE NULL END ) AS "to_do_projects",
    #   ARRAY_AGG(CASE WHEN "projects_project"."status" = 1 THEN "projects_project"."name" ELSE NULL END ) AS "in_progress_projects",
    #   ARRAY_AGG(CASE WHEN "projects_project"."status" = 2 THEN "projects_project"."name" ELSE NULL END ) AS "completed_projects"
    # FROM "users_customuser"
    # LEFT OUTER JOIN "projects_projectmember" ON ("users_customuser"."id" = "projects_projectmember"."member_id")
    # LEFT OUTER JOIN "projects_project" ON ("projects_projectmember"."project_id" = "projects_project"."id")
    # GROUP BY "users_customuser"."id"

    users_qs = (
        get_user_model().objects
        .annotate(
            to_do_projects=ArrayAgg(
                Case(
                    When(
                        projectmember__project__status=project_models.Project.TO_BE_STARTED,
                        then='projectmember__project__name'
                    ),
                    output_field=CharField()
                ),
            ),
            in_progress_projects=ArrayAgg(
                Case(
                    When(
                        projectmember__project__status=project_models.Project.IN_PROGRESS,
                        then='projectmember__project__name'
                    ),
                    output_field=CharField()
                ),  
            ),
            completed_projects=ArrayAgg(
                Case(
                    When(
                        projectmember__project__status=project_models.Project.COMPLETED,
                        then='projectmember__project__name'
                    ),
                    output_field=CharField()
                ),
            )
        )
        .values('first_name', 'last_name', 'email', 'to_do_projects', 'in_progress_projects', 'completed_projects')
    )

    return json.loads(json.dumps(user_serializers.UserWiseProjectSerializer(users_qs, many=True).data))
