import os
from django import template
from django.template.defaultfilters import escapejs

register = template.Library()

"""
    Will be included in 1.4
"""
    
@register.filter()
def escapejsSeq(value):
    return map( escapejs, value );    