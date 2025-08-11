from django.views.generic import TemplateView
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('products/create/', views.product_create, name='product_create'),
    re_path(r'^products/(?P<slug>[-\w\u0600-\u06FF]+)/update/$', views.product_update, name='product_update'),
    re_path(r'^products/(?P<slug>[-\w\u0600-\u06FF]+)/delete/$', views.product_delete, name='product_delete'),
    re_path(r'^products/(?P<slug>[-\w\u0600-\u06FF]+)/$', views.product_detail, name='product_detail'),
    path('products/<int:pk>/toggle-availability/', views.product_toggle_availability, name='product_toggle_availability'),
    path('products/', views.product_list, name='product_list'),
    path('category/add/', views.category_add, name='category_add'),
    path('tag/add/', views.tag_add, name='tag_add'),
    path('', TemplateView.as_view(template_name='404.html'), name='not_found'),
]
