from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
@stringfilter
def italic_first(value):
    """Splits the line and makes first element italic (<i> tag)"""
    parts = value.split()
    result = italify(value) if len(parts) == 1 else f"{italify(parts[0])} {' '.join(parts[1:])}"
    return mark_safe(result)


def italify(value):
    return f'<i>{value}</i>'
