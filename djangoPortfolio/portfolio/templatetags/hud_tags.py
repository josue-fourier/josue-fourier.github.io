from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def short_timesince(value):
    """
    Returns only the most significant unit of timesince.
    e.g., "3 days, 18 hours" -> "3 days"
    """
    if not value:
        return ""
    full_str = timesince(value)
    return full_str.split(',')[0]
