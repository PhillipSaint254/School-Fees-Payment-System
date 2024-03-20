from django import template

register = template.Library()


@register.filter(name='count_characters')
def count_characters(value):
    return len(value)


@register.filter(name='progress_bar')
def progress_bar(balance, full):
    return round((balance/full) * 100, 2)
