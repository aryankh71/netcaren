from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Post
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import CommentForm



def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(request, 'post_detail.html', {'post': post})


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
                    'is_reply': bool(parent_id)
                })
            return redirect('post_detail', slug=post_slug)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'روش درخواست نامعتبر است.'}, status=400)
    return redirect('post_detail', slug=post_slug)