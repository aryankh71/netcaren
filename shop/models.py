# shop/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from slugify import slugify
from django_ckeditor_5.fields import CKEditor5Field

def persian_slugify(text):
    return slugify(text, separator="-", allow_unicode=True)

def generate_barcodes(product, quantity):
    first_letter = product.name[0].upper() if product.name else 'P'
    brand = product.brand.upper() if product.brand else 'UNKNOWN'
    prefix = f"{first_letter}-{brand}-"

    # پیدا کردن آخرین شماره برای این پیشوند
    last_item = InventoryItem.objects.filter(barcode__startswith=prefix).order_by('-barcode').first()
    last_number = 0
    if last_item:
        last_number = int(last_item.barcode.split('-')[-1])

    barcodes = []
    for i in range(1, quantity + 1):
        new_number = last_number + i
        barcode = prefix + f"{new_number:06d}"
        barcodes.append(barcode)

    return barcodes

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    brand = models.CharField(max_length=100, verbose_name="برند")
    
    slug = models.SlugField(
    max_length=200, 
    unique=True, 
    verbose_name="اسلاگ", 
    allow_unicode=True
)
    description = CKEditor5Field(verbose_name='توضیحات', config_name='default')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی سیستمی")
    is_available = models.BooleanField(default=True, verbose_name="موجود است؟")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name="دسته‌بندی")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="برچسب‌ها")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True, verbose_name="تصویر محصول")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="ایجاد شده توسط")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

def save(self, *args, **kwargs):
    if not self.slug:
        # ترکیب نام و برند و ساخت اسلاگ پایه
        base_slug = persian_slugify(f"{self.name}-{self.brand}")
        slug = base_slug
        counter = 1
        # بررسی یکتا بودن اسلاگ
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug

    super().save(*args, **kwargs)

    # مدیریت InventoryItem
    is_new = self.pk is None or not InventoryItem.objects.filter(product=self).exists()
    if is_new or 'stock' in kwargs.get('update_fields', []):
        current_items = InventoryItem.objects.filter(product=self, is_sold=False)
        current_count = current_items.count()
        if self.stock > current_count:
            additional_barcodes = generate_barcodes(self, self.stock - current_count)
            for barcode in additional_barcodes:
                InventoryItem.objects.create(product=self, barcode=barcode)
        elif self.stock < current_count:
            items_to_delete = current_items[self.stock:]
            for item in items_to_delete:
                item.delete()

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="اسلاگ")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام برچسب")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="اسلاگ")

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_items', verbose_name="محصول")
    barcode = models.CharField(max_length=50, unique=True, verbose_name="بارکد")
    is_sold = models.BooleanField(default=False, verbose_name="فروخته شده؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "آیتم موجودی فیزیکی"
        verbose_name_plural = "آیتم‌های موجودی فیزیکی"

    def __str__(self):
        return f"{self.barcode} - {self.product.name}"
    



class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"سبد خرید {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')


    def __str__(self):
        return f"آیتم های انتخاب شده {self.cart.user}"
    


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('completed', 'تکمیل شده'),
        ('canceled', 'لغو شده'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # قیمت لحظه ثبت سفارش

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        return self.quantity * self.price