# core/urls.py

from django.urls import path

from . import views


urlpatterns = [
    # Mapa y consulta AJAX de horarios
    path(
        "mapa/",
        views.mapa_plazas,
        name="mapa_plazas",
    ),
    path(
        "plazos/<int:plaza_id>/",
        views.obtener_plazos_plaza,
        name="obtener_plazos_plaza",
    ),

    # Reservas de clientes
    path(
        "plazas/",
        views.listar_plazas,
        name="listar_plazas",
    ),
    path(
        "mis-reservas/",
        views.mis_reservas,
        name="mis_reservas",
    ),
    path(
        "reserva/nueva/",
        views.crear_reserva,
        name="crear_reserva_general",
    ),
    path(
        "reserva/<int:plazo_id>/",
        views.crear_reserva,
        name="crear_reserva",
    ),
    path(
        "reserva/<int:pk>/cancelar/",
        views.cancelar_reserva_cliente,
        name="cancelar_reserva_cliente",
    ),

    # Administración
    path(
        "admin/gestionar-plazas/",
        views.gestionar_plazas,
        name="gestionar_plazas",
    ),
    path(
        "admin/gestionar-plazas/nueva/",
        views.crear_plaza_admin,
        name="crear_plaza_admin",
    ),
    path(
        "admin/reservas/",
        views.listar_reservas_admin,
        name="listar_reservas_admin",
    ),
    path(
        "admin/plaza/<int:pk>/cancelar/",
        views.cancelar_reserva_admin,
        name="cancelar_reserva_admin",
    ),
]
