from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get a dictionary value by key."""
    return dictionary.get(key) 

@register.filter
def split(value, delimiter):
    """Split a string by a delimiter and return a list."""
    return value.split(delimiter) 