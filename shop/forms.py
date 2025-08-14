from django import forms
from .models import *
# from ckeditor.widgets import CKEditorWidget


class ProductForm(forms.ModelForm):
    # description = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Product
        fields = ['name', 'brand', 'description', 'price', 'stock', 'is_available', 'category', 'tags', 'image', 'slug']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['product', 'barcode','is_sold']