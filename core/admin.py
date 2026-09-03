from django.contrib import admin
from .models import Plaza, Reserva, Plazo

# Register your models here.


@admin.register(Plaza)
class PlazaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nivel', 'pixel_x', 'pixel_y', 'activo']
    list_filter = ['nivel', 'activo']
    search_fields = ['numero']
    fieldsets = (
        ('Información', {'fields': ('numero', 'nivel', 'activo')}),
        ('Posición en el Plano', {'fields': ('pixel_x', 'pixel_y', 'radio')}),
    )

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'plazo', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente__usuario__username',)
    ordering = ['-fecha_creacion']
