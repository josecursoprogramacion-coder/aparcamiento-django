from django.urls import path
from . import views

urlpatterns = [
    path('plazas/', views.listar_plazas, name='listar_plazas'),
    path('admin/gestionar-plazas/', views.gestionar_plazas, name='gestionar_plazas'),
    path('admin/gestionar-plazas/nueva/', views.crear_plaza_admin, name='crear_plaza_admin'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('reserva/nueva/', views.crear_reserva, name='crear_reserva_general'),
    path('reserva/<int:plazo_id>/', views.crear_reserva, name='crear_reserva'),
    path('admin/reservas/', views.listar_reservas_admin, name='listar_reservas_admin'),
    path('admin/plaza/<int:pk>/cancelar/', views.cancelar_reserva_admin, name='cancelar_reserva_admin'),
    path('mapa/', views.mapa_plazas, name='mapa_plazas'),
]
