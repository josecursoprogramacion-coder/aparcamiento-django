from django.urls import path
from . import views

urlpatterns = [
    path('plazas/', views.listar_plazas, name='listar_plazas'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('reserva/<int:plazo_id>/', views.crear_reserva, name='crear_reserva'),
    path('admin/reservas/', views.listar_reservas_admin, name='listar_reservas_admin'),
    path('admin/plaza/<int:pk>/cancelar/', views.cancelar_reserva_admin, name='cancelar_reserva_admin'),
]
