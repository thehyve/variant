from django import template

register = template.Library()

"""
    Will be included in 1.4
"""

@register.filter()
def getsearchresultsize(value):
    """
        Expects a variable of the following structure:
        {
            'key1':formSet1,
            'key2':formSet2,
            'key3':formSet3, 
            ... 
        }
        Returns an integer computed by:
        len(formSet1)+len(formSet2)+len(formSet3)+...
    """
    try:
        s = 0
        for key in value:
            if not value[key] == None:
                s += len(value[key])
        return s  
    except Exception as inst:
        print 'getsearchresultsize exception:',inst
        return '?'