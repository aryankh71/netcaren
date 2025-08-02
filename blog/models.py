from django.db import models
from accounts.models import User
from slugify import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse


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