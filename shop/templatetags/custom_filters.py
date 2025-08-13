from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    return value * arg


@register.filter
def mul(value, arg):
    """ضرب کردن دو عدد"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''