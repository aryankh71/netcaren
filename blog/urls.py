from django.urls import re_path, path
from .views import *

# app_name = 'blog'
urlpatterns = [
    # مسیرهای خاص‌تر
    path('search/', search_view, name='search'),
    path('posts/', post_list, name='post_list'),
    path('posts/add/', post_create, name='post_create'),
    path('posts/<int:pk>/edit/', post_update, name='post_update'),
    path('posts/<int:pk>/delete/', post_delete, name='post_delete'),
    path('post/<int:pk>/toggle-publish/', post_toggle_publish, name='post_toggle_publish'),
    # مسیرهای کامنت
    re_path(r'^post/(?P<post_slug>[\w-]+)/comment/(?P<parent_id>[0-9]+)/$', add_comment, name='add_comment'),
    re_path(r'^post/(?P<post_slug>[\w-]+)/comment/$', add_comment, name='add_comment'),

    # مسیر کلی برای جزئیات پست — آخر قرار بگیره
    re_path(r'^(?P<slug>[\w-]+)/$', post_detail, name='post_detail'),
]
