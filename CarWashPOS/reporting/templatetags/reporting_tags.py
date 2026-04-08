from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Access a dict value by a variable key. Usage: {{ my_dict|get_item:variable }}"""
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)


@register.filter
def format_decimal(value):
    """Return '-' for None, otherwise return the value unlocalized. Usage: {{ amount|format_decimal }}"""
    if value is None:
        return "-"
    return str(value)
