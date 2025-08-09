from django.urls import path
from .views import *

# app_name = 'blog'
urlpatterns = [
    path('posts/', post_list, name='post_list'),
    path('posts/add/', post_create, name='post_create'),
    path('posts/<int:pk>/edit/', post_update, name='post_update'),
    path('posts/<int:pk>/delete/', post_delete, name='post_delete'),
    path('post/<int:pk>/toggle-publish/', post_toggle_publish, name='post_toggle_publish'),
]
