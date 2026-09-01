from django.contrib import admin
from .models import Plaza, Reserva

# Register your models here.


@admin.register(Plaza)
class PlazaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'precio', 'ocupada')
    list_filter = ('tipo', 'ocupada')
    search_fields = ('numero',)
    actions = ['marcar_como_ocupada', 'marcar_como_libre']
    
    @admin.action(description="Marcar seleccionadas como ocupadas")
    def marcar_como_ocupada(self, request, queryset):
        queryset.update(ocupada=True)
    
    @admin.action(description="Marcar seleccionadas como libres")
    def marcar_como_libre(self, request, queryset):
        queryset.update(ocupada=False)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('plaza', 'vehiculo', 'dia', 'fecha_creacion')
    list_filter = ('dia', 'plaza__tipo')
    search_fields = ('plaza__numero', 'vehiculo__matricula')
    ordering = ['-dia']
