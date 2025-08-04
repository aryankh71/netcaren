from django.db import models
from accounts.models import User
from slugify import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse
from django.conf import settings




def persian_slugify(text):
    return slugify(text, separator="-", transliterate=False, allow_unicode=True)

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان')
    content = CKEditor5Field(verbose_name='محتوا', config_name='default')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='نویسنده')
    published_at = models.DateTimeField(verbose_name='تاریخ انتشار')
    is_published = models.BooleanField(default=False, verbose_name='منتشر شده؟')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name='آدرس یکتا')
    image = models.ImageField(upload_to='posts/images/',blank=True, verbose_name='تصویر')

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = persian_slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'

    def __str__(self):
        return self.title



class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments'
    )
    body = models.TextField(max_length=1000, help_text='متن کامنت (حداکثر 1000 کاراکتر)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    class Meta:
        ordering = ['created_at']  # مرتب‌سازی پیش‌فرض بر اساس زمان ایجاد
        indexes = [
            models.Index(fields=['post', 'created_at']),  # ایندکس برای بهبود عملکرد
            models.Index(fields=['parent']),  # ایندکس برای ریپلای‌ها
        ]

    def __str__(self):
        return f'Comment by {self.author or "Anonymous"} on {self.post.title}'

    def can_reply(self, user):
        """چک می‌کند که آیا کاربر می‌تواند به این کامنت پاسخ دهد."""
        if not user.is_authenticated:
            return False
        # فقط نویسنده پست (ادمین) می‌تواند ریپلای کند
        return user == self.post.author