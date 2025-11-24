from django import template
register = template.Library()


@register.filter
def get_item(value, arg):
    return value.get(arg)


@register.filter
def get_attr(value, arg):
    return getattr(value, arg)
