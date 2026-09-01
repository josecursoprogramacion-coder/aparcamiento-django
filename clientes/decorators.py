# clientes/decorators.py

from django.contrib.auth.decorators import user_passes_test
from .models import Cliente

def es_establecimiento(user):
    return (
        user.is_superuser or
        user.groups.filter(name="Establecimientos").exists()
    )

establecimiento_required = user_passes_test(
    es_establecimiento,
    login_url='inicio'  # ← Asegúrate de que esta URL exista
)