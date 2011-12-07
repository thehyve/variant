from django import template

register = template.Library()

"""
    Will be included in 1.4
"""

@register.filter()
def tosnpref(value):
    try:
        #print 'tosnpref received',value
        if value.startswith('rs'):
               value = value.strip('rs')
        #print 'tosnpref returns',value
        return value
    except:
        return value