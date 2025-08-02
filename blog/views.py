from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Post
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import strip_tags



def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(request, 'post_detail.html', {'post': post})


def search_view(request):
    query = request.GET.get('q', '')
    results = Post.objects.filter(
        Q(title__icontains=query),
        is_published=True
    )[:10] if query else []
    print("output==>", results)

    return render(request, 'search_results.html', {'query': query, 'results': results})