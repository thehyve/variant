from django import template

register = template.Library()

@register.filter()
def repeat(value, times):
    try:
        if value == None or len(value) == 0:
            return value
        t = 0
        ret_str = ''
        while t < times:
            ret_str += "{0}".format(value)
            t += 1
        return ret_str
    except Exception:
        return value