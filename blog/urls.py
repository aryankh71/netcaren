from django.urls import re_path, path
from .views import search_view, post_detail, add_comment

# app_name = 'blog'
urlpatterns = [
    # مسیر برای جستجو
    path('search/', search_view, name='search'),

    # مسیر برای افزودن کامنت و ریپلای
    re_path(r'^post/(?P<post_slug>[\w-]+)/comment/(?P<parent_id>[0-9]+)/$', add_comment, name='add_comment'),
    re_path(r'^post/(?P<post_slug>[\w-]+)/comment/$', add_comment, name='add_comment'),

    # مسیر برای نمایش جزئیات پست
    re_path(r'^(?P<slug>[\w-]+)/$', post_detail, name='post_detail'),
]