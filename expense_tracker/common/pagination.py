from rest_framework.pagination import CursorPagination as BaseCursorPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CursorPagination(BaseCursorPagination):
    """
    Cursor-based pagination for stable, performant paging over large datasets.
    Prevents duplicate/missing rows under concurrent writes.
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })
