from django.views.generic import TemplateView
from django.urls import path, re_path
from . import views

urlpatterns = [
    # Products CRUD
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/toggle-availability/', views.product_toggle_availability, name='product_toggle_availability'),
    re_path(r'^products/(?P<slug>[-\w\u0600-\u06FF]+)/update/$', views.product_update, name='product_update'),
    re_path(r'^products/(?P<slug>[-\w\u0600-\u06FF]+)/delete/$', views.product_delete, name='product_delete'),
    re_path(r'^products/(?P<slug>[-\w\u0600-\u06FF]+)/$', views.product_detail, name='product_detail'),
    path('products/', views.product_list, name='product_list'),

    # Category & Tag
    path('category/add/', views.category_add, name='category_add'),
    path('tag/add/', views.tag_add, name='tag_add'),

    # Cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/transfer/', views.transfer_cart, name='transfer_cart'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/',views.order_detail, name='order_detail'),

    # Fallback 404
    path('', TemplateView.as_view(template_name='404.html'), name='not_found'),
]