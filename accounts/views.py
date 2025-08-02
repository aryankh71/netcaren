from django.shortcuts import render, redirect
from django.contrib.auth import login
from accounts.forms import CustomerRegistrationForm, AccountUpdateForm
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from blog.models import Post
from django.utils.timezone import now
from django.contrib.auth import login
from django.utils import timezone




def register_view(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # user.is_active = False  # غیرفعال کردن موقت تا تایید ایمیل
            group, created = Group.objects.get_or_create(name='customers')
            user.groups.add(group)
            login(request, user)
            return redirect('home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form':form})
    


def home_view(request):
    today = timezone.now().date()
    # مقالات امروز (برای بخش جدیدترین مقالات)
    latest_posts = Post.objects.filter(
        is_published=True,
        published_at__date=today
    ).order_by('-published_at')
    # همه مقالات منتشرشده
    all_posts = Post.objects.filter(is_published=True).order_by('-published_at')

    context = {
        'login_form': AuthenticationForm(),
        'register_form': UserCreationForm(),
        'latest_posts': latest_posts,
        'all_posts': all_posts,
    }
    return render(request, 'home.html', context)


@login_required
def account(request):
    user = request.user

    if request.method == 'POST':
        form = AccountUpdateForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save(commit=False)

            # در صورت وارد شدن رمز جدید، آن را تنظیم کن
            password = form.cleaned_data.get('password1')
            if password:
                user.set_password(password)

            user.save()

            # اگر رمز تغییر کرده، سشن کاربر رو آپدیت کن تا لاگ‌اوت نشه
            if password:
                update_session_auth_hash(request, user)

            messages.success(request, 'تغییرات با موفقیت اعمال شد.')
            return redirect('account')
    else:
        form = AccountUpdateForm(instance=user)

    return render(request, 'accounts/account.html', {'form': form})


def login_view(request):
    # بعد از لاگین موفق:
    messages.success(request, f"خوش آمدید {request.user.first_name} {request.user.last_name} عزیز! ثبت‌نام شما با موفقیت انجام شد.")
    return redirect('home')