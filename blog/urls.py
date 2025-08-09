from django.urls import re_path, path
from .views import *

# app_name = 'blog'
urlpatterns = [
    # مسیرهای خاص‌تر
    path('search/', search_view, name='search'),
    # مسیرهای کامنت
    re_path(r'^post/(?P<post_slug>[\w-]+)/comment/(?P<parent_id>[0-9]+)/$', add_comment, name='add_comment'),
    re_path(r'^post/(?P<post_slug>[\w-]+)/comment/$', add_comment, name='add_comment'),

    # مسیر کلی برای جزئیات پست — آخر قرار بگیره
    re_path(r'^(?P<slug>[\w-]+)/$', post_detail, name='post_detail'),
]
