from django import template

register = template.Library()

"""
    Will be included in 1.4
"""

def filterNonEmpty(a): return len(a) > 0

@register.filter()
def joinNonEmpty(value, arg):
    return arg.join(filter( filterNonEmpty, value ))