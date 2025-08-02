from django import template

register = template.Library()

@register.filter(name='add_attrs')
def add_attrs(field, args):
    if not hasattr(field, 'as_widget'):
        return field

    attrs = {}
    for arg in args.split(','):
        if ':' in arg:
            key, value = arg.split(':', 1)
            attrs[key.strip()] = value.strip()
        else:
            # اگر فقط class داده شده باشه
            existing_class = field.field.widget.attrs.get('class', '')
            attrs['class'] = (existing_class + ' ' + arg.strip()).strip()
    return field.as_widget(attrs=attrs)

@register.filter(name='add_placeholder')
def add_placeholder(field, placeholder):
    if hasattr(field, 'as_widget'):
        existing_class = field.field.widget.attrs.get('class', '')
        return field.as_widget(attrs={
            'placeholder': placeholder,
            'class': (existing_class + ' form-control').strip()
        })
    return field  # در صورتی که field یک رشته معمولی باشه
