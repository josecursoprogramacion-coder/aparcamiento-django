from django import template
from clientes.decorators import es_establecimiento

register = template.Library()

@register.filter
def is_establecimiento(user):
    return es_establecimiento(user)
