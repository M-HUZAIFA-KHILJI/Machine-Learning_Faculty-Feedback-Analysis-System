from django import template

register = template.Library()


@register.filter
def initials(name):
    """Return up to two uppercase initials for a given full name."""
    if not name:
        return "?"
    parts = [p for p in name.split() if p]
    if len(parts) == 1:
        return parts[0][0].upper()
    # take first letter of first and last parts
    first = parts[0][0].upper()
    last = parts[-1][0].upper()
    return f"{first}{last}"
