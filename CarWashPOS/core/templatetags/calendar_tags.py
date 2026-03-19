from django import template
from datetime import date

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """Template filter to look up dictionary values by key."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def parse_date(value):
    """Parse an ISO date string (YYYY-MM-DD) into a date object for use with the |date filter."""
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return value
