from django import template
register = template.Library()
 
"""
 From:
 http://twigstechtips.blogspot.com/2010/02/django-filter-to-check-if-string.html
""" 
@register.filter()
def contains(value, arg):
    value = str(value)
    arg = str(arg)
    """
    Usage:
    {% if text|contains:"http://" %}
    This is a link.
    {% else %}
    Not a link.
    {% endif %}
    """
     
    return arg in value
    
    
@register.filter()
def containedin(value, arg):
    #print '\nentered containedin'
    #print "Value:",value
    #print "Arg:",arg
    if value == None:
        #print 'leaving containedin'
        return False
    v = str(value)
    a = []
    for item in arg:
        a.append(str(item))
    v = v.lower()
    for item in a:
        i = item.lower()
        #print i, 'in', v, '?'
        if i in v:
            #print 'True'
            #print 'leaving containedin'
            return True
    #print 'False'
    #print 'leaving containedin'
    return False