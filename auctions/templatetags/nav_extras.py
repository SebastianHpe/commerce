from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def nav_link(context, url_name: str, label: str) -> str:
    """
    Render a Bootstrap nav link and automatically highlight it if active.

    Args:
        context: Template context (needed for request).
        url_name: The URL pattern name (e.g. "index").
        label: The text for the link.

    Returns:
        str: An <a> HTML element with active class if current page matches.
    """
    request = context.get("request")
    try:
        url = reverse(url_name)
    except NoReverseMatch:
        return f'<span class="text-danger">Invalid link: {url_name}</span>'

    active_class = ""
    if request and hasattr(request, "resolver_match"):
        if request.resolver_match.url_name == url_name:
            active_class = " active"

    html = f'<a class="nav-item nav-link{active_class}" href="{url}">{label}</a>'
    return mark_safe(html)