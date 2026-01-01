from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "current_page": self.page.number,
                "page_size": self.page.paginator.per_page,
            }
        )
