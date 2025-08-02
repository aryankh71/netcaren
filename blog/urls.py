from django.urls import re_path, path
from .views import *


# app_name='blog'
urlpatterns = [
    path('search/',search_view, name='search'),
    re_path(r'^(?P<slug>[-\w]+)/$', post_detail, name='post_detail'),

]