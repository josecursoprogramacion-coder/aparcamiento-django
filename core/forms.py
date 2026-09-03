# core/forms.py

from django import forms
from django.utils import timezone

from clientes.models import Vehiculo

from .models import Plaza, Plazo, Reserva


class ReservaForm(forms.ModelForm):
    vehiculo = forms.ModelChoiceField(
        queryset=Vehiculo.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="🚗 Selecciona tu vehículo",
    )

    class Meta:
        model = Reserva
        fields = ["vehiculo", "plazo"]
        widgets = {
            "plazo": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "plazo": "🕒 Franja horaria (plaza y fecha)",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["plazo"].queryset = (
            Plazo.objects
            .filter(
                disponible=True,
                fecha__gte=timezone.localdate(),
                plaza__activo=True,
                plaza__nivel__in=[
                    Plaza.PLANTA_0,
                    Plaza.SOTANO_1,
                    Plaza.SOTANO_2,
                ],
                plaza__numero__gte=1,
                plaza__numero__lte=10,
            )
            .select_related("plaza")
            .order_by(
                "fecha",
                "horario_desde",
                "plaza__nivel",
                "plaza__numero",
            )
        )

        if user and hasattr(user, "cliente_perfil"):
            self.fields["vehiculo"].queryset = (
                Vehiculo.objects
                .filter(cliente=user.cliente_perfil)
                .order_by("pk")
            )


class PlazaForm(forms.ModelForm):
    """
    Alta administrativa de una plaza.

    Las coordenadas y el radio no se solicitan porque views.py los asigna
    automáticamente desde MAPA_PLAZAS según nivel + número.
    """

    class Meta:
        model = Plaza
        fields = ["numero", "nivel", "activo"]
        widgets = {
            "numero": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 10,
                }
            ),
            "nivel": forms.Select(
                attrs={"class": "form-select"}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_numero(self):
        numero = self.cleaned_data["numero"]

        if not 1 <= numero <= 10:
            raise forms.ValidationError(
                "El número de plaza debe estar entre 1 y 10."
            )

        return numero

    def clean(self):
        cleaned_data = super().clean()

        numero = cleaned_data.get("numero")
        nivel = cleaned_data.get("nivel")

        if numero is None or not nivel:
            return cleaned_data

        repetida = Plaza.objects.filter(
            numero=numero,
            nivel=nivel,
        )

        if self.instance.pk:
            repetida = repetida.exclude(pk=self.instance.pk)

        if repetida.exists():
            raise forms.ValidationError(
                f"Ya existe la plaza {numero} en {nivel}."
            )

        return cleaned_data
