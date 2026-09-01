# clientes/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    
    # Vehículos
    path('mis-vehiculos/', views.mis_vehiculos, name='mis_vehiculos'),
    path('nuevo-vehiculo/', views.nuevo_vehiculo, name='nuevo_vehiculo'),
    
    # Edición y Eliminación de vehículos
    path('vehiculo/editar/<int:pk>/', views.editar_vehiculo, name='editar_vehiculo'),
    path('vehiculo/eliminar/<int:pk>/', views.eliminar_vehiculo, name='eliminar_vehiculo'),
    
    # Clientes
    path('crear-cliente/', views.crear_cliente, name='crear_cliente'),
]