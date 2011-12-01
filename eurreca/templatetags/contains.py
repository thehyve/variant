from django import template
register = template.Library()
 
"""
 From:
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
    value = str(value)
    arg = str(arg)
    return arg in value
    
    
@register.filter()
def containedin(value, arg):
    if value == None:
        return False
    v = str(value)
    a = []
    for item in arg:
        a.append(str(item))
    v = v.lower()
    for item in a:
        i = item.lower()
        if i in v:
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
    a = []
    for item in arg:
        a.append(str(item))
    v = v.lower()
    for item in a:
        i = item.lower()
        if i in v:
            return True
    return False