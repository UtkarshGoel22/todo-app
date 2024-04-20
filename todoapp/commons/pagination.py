from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Generic Pagination class.
    """

    page_size = 10
