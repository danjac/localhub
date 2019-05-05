from django.conf import settings

PAGINATE_BY = getattr(settings, 'COMMUNIKIT_CONTENT_PAGINATE_BY', 12)
