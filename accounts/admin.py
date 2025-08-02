from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'get_groups', 'is_superuser', 'is_active')
    list_filter = ('is_superuser', 'groups')

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'گروه‌ها'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # فقط وقتی فیلتر is_superuser ست نشده باشه، سوپریوزرها رو حذف کن
        is_superuser_filter = request.GET.get('is_superuser')
        if is_superuser_filter is None:
            return qs.exclude(is_superuser=True)
        return qs