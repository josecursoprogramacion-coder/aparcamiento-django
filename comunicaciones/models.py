from django.db import models
from django.contrib.auth.models import User
import uuid
import random


class MensajeEnviado(models.Model):
    """Registra cada mensaje enviado al cliente"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_comunicaciones')
    tipo = models.CharField(
        max_length=30,
        choices=[
            ('instrucciones_taquilla', 'Instrucciones Taquilla'),
            ('codigo_apertura', 'Código de Apertura'),
            ('enlace_parking', 'Enlace al Parking'),
        ]
    )
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_envio']


class CodigoTaquilla(models.Model):
    """Códigos de apertura de la taquilla (4 dígitos)"""
    codigo = models.CharField(max_length=4, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_uso = models.DateTimeField(null=True, blank=True)
    usado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Código {self.codigo} - {'Activo' if self.activo else 'Usado'}"
    
    @classmethod
    def generar_codigo(cls):
        """Genera un código único de 4 dígitos"""
        while True:
            codigo = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            if not cls.objects.filter(codigo=codigo).exists():
                return cls.objects.create(codigo=codigo)


class Resena(models.Model):
    """Reseñas de los clientes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resenas_comunicaciones')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    respondida = models.BooleanField(default=False)
    respuesta = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Reseña {self.rating}⭐ de {self.user.username}"