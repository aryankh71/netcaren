from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.http import JsonResponse
from blog.forms import *
from django.contrib.auth import get_user_model
from django.db import transaction
from content_management.decorators import staff_required_view



# لیست محصولات
@staff_required_view
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

# جزئیات محصول
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    comment_form = CommentForm(request.POST or None)
    
    if request.method == 'POST' and comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.product = product
        comment.author = request.user
        comment.save()
        return JsonResponse({
            'id': comment.id,
            'author': comment.author.username,
            'body': comment.body,
            'created_at': comment.created_at.strftime('%Y/%m/%d %H:%M'),
            'is_reply': False
        })
    
    # مسیر پیش‌فرض برای GET یا فرم نامعتبر
    return render(request, 'product_detail.html', {
        'product': product,
        'comment_form': comment_form
    })
# ایجاد محصول جدید
@staff_required_view
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
@staff_required_view
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})

# حذف محصول
@staff_required_view
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})


@staff_required_view
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_create')  # برگرد به صفحه افزودن محصول
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})


@staff_required_view
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



@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    products = []
    total = 0

    for item in cart.items.all():
        subtotal = item.product.price * item.quantity
        products.append({
            'product': item.product,
            'quantity': item.quantity,
            'subtotal': subtotal
        })
        total += subtotal

    return render(request, 'cart.html', {'products': products, 'total': total})

# -----------------------------
# اضافه کردن محصول به سبد
# -----------------------------
@login_required
def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_view')

# -----------------------------
# حذف محصول از سبد
# -----------------------------
@login_required
def remove_from_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = cart.items.filter(product_id=product_id).first()
    if item:
        item.delete()
    return redirect('cart_view')

# -----------------------------
# تغییر تعداد محصول
# -----------------------------
@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item = cart.items.filter(product_id=product_id).first()
        if cart_item:
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
    return redirect('cart_view')

# -----------------------------
# تسویه حساب
# -----------------------------
@login_required
@transaction.atomic
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        return render(request, 'cart.html', {'error': "سبد خرید شما خالی است"})

    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        total = 0

        for item in cart.items.all():
            if item.quantity > item.product.stock:
                return render(request, 'cart.html', {'error': f"موجودی {item.product.name} کافی نیست"})

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            total += item.product.price * item.quantity
            item.product.stock -= item.quantity
            item.product.save()

        order.total_price = total
        order.save()

        # پاک کردن آیتم‌های سبد بعد از ثبت سفارش
        cart.items.all().delete()
        return redirect('order_detail', order_id=order.id)

    return render(request, 'checkout.html', {'cart': cart})

# -----------------------------
# جزئیات سفارش
# -----------------------------
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})