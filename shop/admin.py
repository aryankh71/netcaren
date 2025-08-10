# shop/admin.py
from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'stock', 'is_available', 'created_at']
    list_filter = ['is_available', 'category']
    search_fields = ['name', 'description', 'brand']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'product', 'is_sold', 'created_at']
    list_filter = ['is_sold']
    search_fields = ['barcode']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}