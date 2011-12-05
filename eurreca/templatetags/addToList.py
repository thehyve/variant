from django import template

register = template.Library()

"""
    Will be included in 1.4
"""

@register.filter()
def addToList(value, arg):
	if( value == "[]" ):
		if( len(arg) == 0 ):
			return []
		else:
			return [ arg ]
	else:
		if( len(arg) > 0 ):
			value.append( arg )
			
		return value
