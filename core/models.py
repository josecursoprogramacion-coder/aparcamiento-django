from django.db import models
from django.utils import timezone
from clientes.models import Vehiculo, Cliente

# core/models.py

class Plaza(models.Model):
    NIVEL_CHOICES = [
        ('Sótano 1', 'Sótano 1'),
        ('Sótano 2', 'Sótano 2'),
        ('Planta 0', 'Planta 0'),
        ('Planta 1', 'Planta 1'),
    ]

    numero = models.IntegerField()
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    
    # Coordenadas en píxeles de la imagen del plano
    # Medidas en Photoshop o similar: (0,0) es la esquina superior-izquierda
    pixel_x = models.IntegerField(default=100, help_text="Posición X en píxeles de la imagen")
    pixel_y = models.IntegerField(default=100, help_text="Posición Y en píxeles de la imagen")
    
    # Tamaño del círculo del marcador (radio en píxeles)
    radio = models.IntegerField(default=15)
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nivel', 'numero']
        unique_together = ('nivel', 'numero')

    def __str__(self):
        return f"{self.nivel} - Plaza {self.numero}"


class Plazo(models.Model):
    plaza = models.ForeignKey(Plaza, on_delete=models.CASCADE, related_name='plazos')
    fecha = models.DateField()
    horario_desde = models.TimeField()
    horario_hasta = models.TimeField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    disponible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['plaza', 'fecha', 'horario_desde']
        verbose_name = 'Plazo disponible'
        verbose_name_plural = 'Plazos disponibles'
    
    def __str__(self):
        return f"{self.plaza} - {self.fecha} ({self.horario_desde}-{self.horario_hasta})"


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='reservas', null=True, blank=True)
    plazo = models.ForeignKey(Plazo, on_delete=models.CASCADE, related_name='reservas', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Reserva #{self.id} - {self.cliente} ({self.estado})"

