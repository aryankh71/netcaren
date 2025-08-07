from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import CommentForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import PostForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone




# def post_detail(request, slug):
#     post = get_object_or_404(Post, slug=slug, is_published=True)
#     return render(request, 'post_detail.html', {'post': post})


# def search_view(request):
#     query = request.GET.get('q', '')
#     results = Post.objects.filter(
#         Q(title__icontains=query),
#         is_published=True
#     )[:10] if query else []
#     print("output==>", results)
#
#     return render(request, 'search_results.html', {'query': query, 'results': results})
def search_view(request):
    query = request.GET.get('q', '')
    results = Post.objects.filter(
        Q(title__icontains=query),
        is_published=True
    )[:10] if query else []

    # اگر درخواست AJAX باشد، پاسخ JSON برگردانید
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        results_data = [
            {
                'title': post.title,
                'url': post.get_absolute_url()  # فرض بر این است که مدل Post متد get_absolute_url دارد
            } for post in results
        ]
        return JsonResponse({'results': results_data})

    # برای درخواست‌های معمولی، قالب HTML رندر کنید
    return render(request, 'search_results.html', {'query': query, 'results': results})



def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comment_form = CommentForm()  # فرم برای کامنت و ریپلای
    comments = post.comments.filter(is_visible=True).select_related('author', 'parent')
    comments_count = comments.count()
    return render(request, 'post_detail.html', {
        'post': post,
        'comment_form': comment_form,
        'comments': comments,
        'comments_count': comments_count
    })

@login_required
def add_comment(request, post_slug, parent_id=None):
    post = get_object_or_404(Post, slug=post_slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id, post=post)
                if not parent.can_reply(request.user):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'error': 'فقط نویسنده پست می‌تواند پاسخ دهد.'}, status=403)
                    return redirect('post_detail', slug=post_slug)
                comment.parent = parent

            comment.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': comment.id,
                    'body': comment.body,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_reply': bool(parent_id),
                    'comments_count': post.comments.filter(is_visible=True).count()
                })
            return redirect('post_detail', slug=post_slug)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'روش درخواست نامعتبر است.'}, status=400)
    return redirect('post_detail', slug=post_slug)



# فقط اجازه به ادمین‌ها (is_staff یا superuser)
def staff_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(staff_required)
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'dashboard/posts/post_list.html', {'posts': posts})

# views.py


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
            return redirect('dashboard:post_list')
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
        return redirect('dashboard:post_list')
    return render(request, 'dashboard/posts/post_form.html', {'form': form, 'post': post})

@user_passes_test(staff_required)
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'مقاله حذف شد.')
        return redirect('dashboard:post_list')
    return render(request, 'dashboard/posts/post_confirm_delete.html', {'post': post})
