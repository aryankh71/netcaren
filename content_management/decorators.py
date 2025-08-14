# app/decorators.py
from functools import wraps
from django.shortcuts import render

def staff_required_view(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
            return render(request, 'errors/404.html', status=404)
        return view_func(request, *args, **kwargs)
    return wrapper
