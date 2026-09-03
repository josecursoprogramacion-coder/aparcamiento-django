from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Plaza(models.Model):
    """
    Plaza física del Parking Catedral.

    El mapa solo utiliza tres plantas y diez plazas seleccionables por planta.
    Las coordenadas se sincronizan desde views.py con los tres planos oficiales.
    """

    SOTANO_1 = "Sótano 1"
    SOTANO_2 = "Sótano 2"
    PLANTA_0 = "Planta 0"

    NIVEL_CHOICES = [
        (PLANTA_0, "Planta 0"),
        (SOTANO_1, "Sótano 1"),
        (SOTANO_2, "Sótano 2"),
    ]

    numero = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)

    # Centro del marcador dentro de la imagen original (1754 x 1240 px).
    # Se conservan en BD para que cada Plaza siga siendo autocontenida.
    pixel_x = models.PositiveIntegerField(default=0)
    pixel_y = models.PositiveIntegerField(default=0)

    # Radio visual del marcador circular.
    radio = models.PositiveSmallIntegerField(default=28)

    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nivel", "numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["nivel", "numero"],
                name="plaza_unica_por_nivel_numero",
            ),
        ]

    def __str__(self):
        return f"{self.nivel} - Plaza {self.numero}"


class Plazo(models.Model):
    plaza = models.ForeignKey(
        Plaza,
        on_delete=models.CASCADE,
        related_name="plazos",
    )
    fecha = models.DateField()
    horario_desde = models.TimeField()
    horario_hasta = models.TimeField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    disponible = models.BooleanField(default=True)

    class Meta:
        ordering = ["plaza", "fecha", "horario_desde"]
        verbose_name = "Plazo disponible"
        verbose_name_plural = "Plazos disponibles"

    def __str__(self):
        return (
            f"{self.plaza} - {self.fecha} "
            f"({self.horario_desde}-{self.horario_hasta})"
        )


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
        ("completada", "Completada"),
    ]

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.CASCADE,
        related_name="reservas",
        null=True,
        blank=True,
    )
    vehiculo = models.ForeignKey(
        "clientes.Vehiculo",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    plazo = models.ForeignKey(
        Plazo,
        on_delete=models.CASCADE,
        related_name="reservas",
        null=True,
        blank=True,
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="pendiente",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Reserva #{self.pk} - {self.cliente} ({self.estado})"

    def esta_expirada(self):
        return (
            self.estado == "pendiente"
            and self.expira_en is not None
            and timezone.now() > self.expira_en
        )

    def cancelar(self):
        """
        Cancela la reserva y vuelve a liberar su plazo cuando no existe
        otra reserva activa para el mismo plazo.
        """
        self.estado = "cancelada"
        self.save(update_fields=["estado"])

        if not self.plazo_id:
            return

        existe_otra_reserva = Reserva.objects.filter(
            plazo_id=self.plazo_id,
            estado__in=["pendiente", "confirmada"],
        ).exclude(pk=self.pk).exists()

        if not existe_otra_reserva:
            self.plazo.disponible = True
            self.plazo.save(update_fields=["disponible"])
