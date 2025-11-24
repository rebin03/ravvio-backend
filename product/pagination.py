from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    """Pagination for product listing with client-controlled page size."""

    # Default page size if client does not specify
    page_size = 10
    # Query parameter name: ?page_size=20
    page_size_query_param = "page_size"
    # Maximum allowed page size to avoid abuse
    max_page_size = 100
