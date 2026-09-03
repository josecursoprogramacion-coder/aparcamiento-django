from django import forms
from .models import Reserva, Plaza, Plazo
from clientes.models import Vehiculo

class ReservaForm(forms.ModelForm):
    vehiculo = forms.ModelChoiceField(
        queryset=Vehiculo.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='🚗 Selecciona tu vehículo'
    )

    class Meta:
        model = Reserva
        fields = ['vehiculo', 'plazo']
        widgets = {
            'plazo': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'plazo': '🕒 Franja Horaria (Plaza y Fecha)'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filtrar plazos disponibles
        self.fields['plazo'].queryset = Plazo.objects.filter(disponible=True)
        # Filtrar vehículos del usuario
        if user and hasattr(user, 'cliente_perfil'):
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(cliente=user.cliente_perfil)

class PlazaForm(forms.ModelForm):
    class Meta:
        model = Plaza
        fields = ['numero', 'nivel', 'pixel_x', 'pixel_y', 'radio', 'activo']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'nivel': forms.Select(attrs={'class': 'form-control'}),
            'pixel_x': forms.NumberInput(attrs={'class': 'form-control'}),
            'pixel_y': forms.NumberInput(attrs={'class': 'form-control'}),
            'radio': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }