from django import template
from django.urls import translate_url
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


@register.simple_tag(takes_context=True)
def url_in_language(context, lang_code):
    """Absolute URL of the current page in another language (for hreflang links)."""
    request = context["request"]
    return request.build_absolute_uri(translate_url(request.path, lang_code))
