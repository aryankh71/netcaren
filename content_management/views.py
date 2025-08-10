from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from blog.models import Post
from blog.forms import PostForm
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *


def staff_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def check_staff_user(request):
    user = request.user
    if not (user.is_authenticated and (user.is_staff or user.is_superuser)):
        return False
    return True


def post_list(request):
    if not check_staff_user(request):
        return render(request, 'errors/404.html', status=404)
    posts = Post.objects.all()
    return render(request, 'dashboard/posts/post_list.html', {'posts': posts})


@require_POST
def post_toggle_publish(request, pk):
    if not check_staff_user(request):
        return JsonResponse({'success': False, 'error': 'دسترسی غیرمجاز'}, status=403)
    try:
        post = Post.objects.get(pk=pk)
        post.is_published = not post.is_published
        if post.is_published and not post.published_at:
            post.published_at = timezone.now()
        post.save()
        return JsonResponse({'success': True, 'is_published': post.is_published})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'پست یافت نشد'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def post_create(request):
    if not check_staff_user(request):
        return render(request, 'errors/404.html', status=404)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # تنظیم نویسنده
            if 'publish' in request.POST:
                post.is_published = True
                if not post.published_at:
                    post.published_at = timezone.now()
            elif 'draft' in request.POST:
                post.is_published = False
                if not post.published_at:
                    post.published_at = timezone.now()
            post.save()
            messages.success(request, 'مقاله با موفقیت ایجاد شد.')
            return redirect('post_list')
        else:
            messages.error(request, 'خطایی در فرم وجود دارد. لطفاً فیلدها را بررسی کنید.')
            print(form.errors)  # برای دیباگ
            print("User:", request.user, "Is authenticated:", request.user.is_authenticated)
    else:
        form = PostForm()
    return render(request, 'dashboard/posts/post_form.html', {'form': form})


def post_update(request, pk):
    if not check_staff_user(request):
        return render(request, 'errors/404.html', status=404)

    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if 'publish' in request.POST:
                post.is_published = True
                if not post.published_at:
                    post.published_at = timezone.now()
            elif 'draft' in request.POST:
                post.is_published = False
                if not post.published_at:
                    post.published_at = timezone.now()
            post.save()
            messages.success(request, 'مقاله با موفقیت ویرایش شد.')
            return redirect('post_list')
        else:
            messages.error(request, 'خطایی در فرم وجود دارد. لطفاً فیلدها را بررسی کنید.')
            print(form.errors)
            print("User:", request.user, "Is authenticated:", request.user.is_authenticated)
    else:
        form = PostForm(instance=post)
    return render(request, 'dashboard/posts/post_form.html', {'form': form, 'post': post})


def post_delete(request, pk):
    if not check_staff_user(request):
        return render(request, 'errors/404.html', status=404)

    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'مقاله حذف شد.')
        return redirect('post_list')
    return render(request, 'dashboard/posts/post_confirm_delete.html', {'post': post})


@csrf_exempt
def post_bulk_action(request):
    if not check_staff_user(request):
        return JsonResponse({'success': False, 'error': 'دسترسی غیرمجاز'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            post_ids = data.get('post_ids', [])
            posts = Post.objects.filter(pk__in=post_ids)
            if action == 'publish':
                posts.update(is_published=True)
            elif action == 'unpublish':
                posts.update(is_published=False)
            elif action == 'delete':
                posts.delete()
            else:
                return JsonResponse({'success': False, 'error': 'عملیات نامعتبر'}, status=400)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'}, status=400)


def dashboard_home(request):
    user = request.user
    if not (user.is_authenticated and (user.is_staff or user.is_superuser)):
        return render(request, 'errors/404.html', status=404)
    return render(request, 'dashboard/dashboard.html')
