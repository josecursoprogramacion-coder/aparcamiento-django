# clientes/models.py

from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente_perfil')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.usuario.username

class Plaza(models.Model):
    numero = models.IntegerField(unique=True)
    nivel = models.CharField(max_length=10, default='Sótano 1')
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nivel', 'numero']
    
    def __str__(self):
        return f"Plaza {self.numero} ({self.nivel})"

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
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='clientes_reservas')
    plaza = models.ForeignKey(Plaza, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    total_precio = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Reserva #{self.id} - {self.cliente} ({self.estado})"
    
    def cancelar(self):
        """Método para cancelar la reserva y liberar la plaza"""
        self.estado = 'cancelada'
        self.save()

# clientes/models.py
class Vehiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='vehiculos')
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    matricula = models.CharField(max_length=8, unique=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['matricula']
    
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.matricula})"



