from django import template

register = template.Library()

"""
    Will be included in 1.4
"""

@register.filter()
def truncatechars(value, length):
    """
        truncate after a certain number of characters,
        if the last character is not space truncate at the next space
    """
    le = length
    if value == None:
        return value
    if len(value) > length:
        try:
            if value[le] == " ":
                return value[:le]
            else:
                while value[le] != " ":
                    le += 1
                else:
                    return value[:le]

        except IndexError:
            return value[:length]
    else:
        return value
