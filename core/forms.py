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

    def clean(self):
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        plaza = cleaned_data.get('plaza')

        if vehiculo and plaza:
            tipo_vehiculo = (vehiculo.tipo or '').lower()
            tipo_plaza = (plaza.tipo or '').lower()

            # Validación de correspondencia de tipos
            if tipo_vehiculo == 'electrico' and tipo_plaza != 'electrico':
                raise forms.ValidationError("🚫 No se puede reservar: Un vehículo eléctrico solo puede estacionarse en plazas de tipo Eléctrico.")
            
            if tipo_vehiculo == 'premium' and tipo_plaza != 'premium':
                raise forms.ValidationError("🚫 No se puede reservar: Un vehículo premium requiere una plaza de tipo Premium.")

            if tipo_vehiculo and tipo_plaza and tipo_vehiculo not in ['turismo', 'otro', '']:
                if tipo_vehiculo != tipo_plaza and tipo_plaza != 'normal':
                    raise forms.ValidationError(f"🚫 No se puede reservar: El tipo de vehículo ('{vehiculo.tipo}') no corresponde con el tipo de la plaza ('{plaza.tipo}').")

        return cleaned_data

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