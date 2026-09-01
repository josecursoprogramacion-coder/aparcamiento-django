from django import template

register = template.Library()

@register.filter(name='dict_item')
def dict_item(dictionary, key):
    if hasattr(dictionary, 'get'):
        item = dictionary.get(key)
        if item and hasattr(item, 'label'):
            return item.label
    return key

@register.filter(name='is_establecimiento')
def is_establecimiento(value):
    """Retorna si el usuario pertenece al grupo o condición de establecimiento."""
    if value is None:
        return False
    if hasattr(value, 'groups'):
        return value.groups.filter(name='establecimiento').exists() or value.is_staff
    return bool(value)
