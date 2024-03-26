from django import template

register = template.Library()


@register.filter(name='count_characters')
def count_characters(value):
    return len(value)


@register.simple_tag
def progress_bar(balance, full):
    return round(((balance - full)/full) * 100, 2)
