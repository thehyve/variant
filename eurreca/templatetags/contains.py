from django import template
register = template.Library()
 
"""
 Based on:
 http://twigstechtips.blogspot.com/2010/02/django-filter-to-check-if-string.html
""" 
@register.filter()
def contains(value, arg):
    '''
    Usage:
    {% if text|contains:"http://" %}
    This is a link.
    {% else %}
    Not a link.
    {% endif %}
    '''
    if isinstance( value, str ) or isinstance( value, unicode ):
        value = value.lower()
    else:
        value = str(value).lower()
    arg = str(arg)
    return arg in value
    
    
@register.filter()
def containedin(value, arg):
    if isinstance( value, str ) or isinstance( value, unicode ):
        value = value.lower()
    else:
        value = str(value).lower()
    if (value in arg):
        return True
    for a in arg:
        if isinstance( a, str ) or isinstance( a, unicode ):
            a = a.lower()
        else:
            a = str(a).lower()
        if a in value:
            return True
    return False
    
@register.filter()
def snprefcontainedin(value, arg):
    ''' Convenience function. Same effect could be reached by combining
    'tosnpref' and 'containedin' filters. '''
    if value == None:
        return False
    v = str(value)
    if v.startswith('rs'):
           v = v.strip('rs')
    return (v in arg)