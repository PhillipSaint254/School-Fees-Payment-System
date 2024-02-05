from django import template

register = template.Library()


@register.filter(name='count_characters')
def count_characters(value):
    return len(value)
