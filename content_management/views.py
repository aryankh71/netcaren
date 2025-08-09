from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from blog.models import Post, Comment
from blog.forms import CommentForm
from django.contrib.auth.decorators import login_required, user_passes_test
from blog.forms import PostForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone


# فقط اجازه به ادمین‌ها (is_staff یا superuser)
def staff_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(staff_required)
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'dashboard/posts/post_list.html', {'posts': posts})



@login_required
@user_passes_test(staff_required)
@require_POST
def post_toggle_publish(request, pk):
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


@user_passes_test(staff_required)
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'مقاله با موفقیت ایجاد شد.')
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'dashboard/posts/post_form.html', {'form': form})

@user_passes_test(staff_required)
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        messages.success(request, 'مقاله با موفقیت ویرایش شد.')
        return redirect('post_list')
    return render(request, 'dashboard/posts/post_form.html', {'form': form, 'post': post})

@user_passes_test(staff_required)
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'مقاله حذف شد.')
        return redirect('post_list')
    return render(request, 'dashboard/posts/post_confirm_delete.html', {'post': post})
