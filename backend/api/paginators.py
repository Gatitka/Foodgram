from rest_framework.pagination import PageNumberPagination

from foodgram.settings import DEFAULT_PAGE_SIZE


class StandardResultsSetPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
