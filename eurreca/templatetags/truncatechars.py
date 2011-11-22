﻿from django import template

register = template.Library()

"""
    Will be included in 1.4
"""

@register.filter()
def truncatechars(value, length):
    """
        truncate after a certain number of characters,
        if the last character is not space truncate at the next space
        
        Edit by Taco: Now adds three dots at the end, and takes those dots
            in to account when checking where to truncate and add the dots.
    """
    le = length-3
    if value == None:
        return value
    if len(value) > length:
        try:
            if value[le] == " ":
                return '{0}...'.format(value[:le])
            else:
                while value[le] != " ":
                    le += 1
                else:
                    return '{0}...'.format(value[:le])

        except IndexError:
            return value[:length]
    else:
        return value
