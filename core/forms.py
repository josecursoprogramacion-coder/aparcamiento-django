from django import forms
from .models import Reserva, Plaza
from clientes.models import Vehiculo

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['vehiculo', 'plaza', 'dia']
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'form-control'}),
            'plaza': forms.Select(attrs={'class': 'form-control'}),
            'dia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filtrar plazas libres usando el modelo Plaza de core
        self.fields['plaza'].queryset = Plaza.objects.filter(ocupada=False)
        # Filtrar solo los vehículos del cliente autenticado
        if user and hasattr(user, 'cliente_perfil'):
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(cliente=user.cliente_perfil)
        else:
            self.fields['vehiculo'].queryset = Vehiculo.objects.none()

class PlazaForm(forms.ModelForm):
    class Meta:
        model = Plaza
        fields = ['numero', 'tipo', 'precio', 'ocupada']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de plaza'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10.00'}),
            'ocupada': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'numero': '🔢 Número de Plaza',
            'tipo': '⚙️ Tipo de Plaza',
            'precio': '💰 Precio por Día (€)',
            'ocupada': '🔴 ¿Está Ocupada?'
        }