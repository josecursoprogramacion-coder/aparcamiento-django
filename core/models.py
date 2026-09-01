from django.db import models
from django.utils import timezone
from clientes.models import Vehiculo, Cliente

class Plaza(models.Model):
    TIPO_CHOICES = [
        ('normal', 'Normal'),
        ('premium', 'Premium'),
        ('electrico', 'Eléctrico'),
    ]
    
    numero = models.IntegerField(unique=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    ocupada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Plaza"
        verbose_name_plural = "Plazas"
        ordering = ['numero']
    
    def __str__(self):
        return f"Plaza {self.numero} ({self.tipo})"

class Reserva(models.Model):
    plaza = models.ForeignKey(Plaza, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    dia = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-dia']
        unique_together = ['plaza', 'dia']  # Evita reservas duplicadas
    
    def __str__(self):
        return f"Reserva {self.plaza.numero} - {self.dia}"
    
    def save(self, *args, **kwargs):
        # Validar que la plaza no esté ocupada ese día
        if Reserva.objects.filter(plaza=self.plaza, dia=self.dia).exclude(pk=self.pk).exists():
            raise ValueError(f"La plaza {self.plaza.numero} ya está reservada para el {self.dia}")
        
        # Marcar la plaza como ocupada
        self.plaza.ocupada = True
        self.plaza.save()
        
        super().save(*args, **kwargs)
    
    def cancelar(self):
        self.plaza.ocupada = False
        self.plaza.save()
        self.delete()

class Plazo(models.Model):
    """
    Representa una franja horaria disponible para reservar en una plaza.
    """
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