from django.db import models
from django.conf import settings
from core.models import Reserva

class Pago(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]

    METODO_CHOICES = [
        ('card', 'Tarjeta'),
        ('bizum', 'Bizum'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]

    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='pago')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pagos')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES, default='card')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default='EUR')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    stripe_error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pago #{self.id} | {self.reserva.plaza.numero} | {self.monto}€ | {self.estado}"

    @property
    def monto_en_centavos(self):
        return int(self.monto * 100)

    @property
    def es_bizum(self):
        return self.metodo_pago == 'bizum'

    @property
    def total_reembolsado(self):
        return sum(r.monto for r in self.reembolsos.filter(estado='completado'))

    @property
    def reembolsable(self):
        return self.monto - self.total_reembolsado


class Reembolso(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
    ]
    MOTIVO_CHOICES = [
        ('duplicate', 'Duplicado'),
        ('fraudulent', 'Fraude'),
        ('requested_by_customer', 'Solicitado por el cliente'),
    ]

    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='reembolsos')
    stripe_refund_id = models.CharField(max_length=255, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=30, choices=MOTIVO_CHOICES)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    gestionado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reembolsos_gestionados')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reembolso #{self.id} de {self.monto}€ (Pago {self.pago.id})"

    @property
    def monto_en_centavos(self):
        return int(self.monto * 100)