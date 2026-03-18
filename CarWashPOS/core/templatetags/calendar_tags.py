from django import template

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """Template filter to look up dictionary values by key."""
    if dictionary is None:
        return None
    return dictionary.get(key)
