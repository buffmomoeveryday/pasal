from django import template

register = template.Library()


@register.filter(name="times")
def times(number):
    return range(number)


@register.filter(name="range")
def filter_range(start, end):
    return range(start, end)




