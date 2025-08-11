from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm, CategoryForm, TagForm
from django.http import JsonResponse



# لیست محصولات
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

# جزئیات محصول
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})

# ایجاد محصول جدید

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            form.save_m2m()  # ذخیره ManyToMany مثل tags
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

# ویرایش محصول
@login_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})

# حذف محصول
@login_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})


def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_create')  # برگرد به صفحه افزودن محصول
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

def tag_add(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_create')
    else:
        form = TagForm()
    return render(request, 'tag_form.html', {'form': form})


def product_toggle_availability(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # می‌توان محدودیت دسترسی اضافه کرد، مثلا فقط کاربر سازنده یا ادمین
    # if request.user != product.created_by and not request.user.is_staff:
    #     return JsonResponse({'success': False, 'error': 'شما اجازه تغییر وضعیت این محصول را ندارید.'}, status=403)

    product.is_available = not product.is_available
    product.save(update_fields=['is_available'])

    return JsonResponse({'success': True, 'is_available': product.is_available})