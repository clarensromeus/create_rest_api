from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


# i could of being used more in-depth pagination customization
# for just a demonstration i slightly customize it
class Limit_offset_pagination(LimitOffsetPagination):
    default_limit = 2,
    max_limit = 5


class Page_numer_pagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 5
