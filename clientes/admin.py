from django.contrib import admin
from .models import Reserva, Plazo, Plaza, Cliente, Vehiculo




@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'plaza', 'fecha_inicio', 'estado']
    search_fields = ['cliente__usuario__username', 'plaza__numero']

@admin.register(Plazo)
class PlazoAdmin(admin.ModelAdmin):
    list_display = ['plaza', 'fecha', 'horario_desde', 'horario_hasta', 'disponible']
    list_filter = ['fecha', 'disponible']

@admin.register(Plaza)
class PlazaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nivel', 'activo']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono']

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['matricula', 'cliente']