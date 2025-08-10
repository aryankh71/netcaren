from django.db import models

class AllowedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)  # فیلد برای ذخیره IP (IPv4 یا IPv6)
    description = models.CharField(max_length=255, blank=True)  # توضیح اختیاری، مثل نام کاربر

    def __str__(self):
        return self.ip_address
