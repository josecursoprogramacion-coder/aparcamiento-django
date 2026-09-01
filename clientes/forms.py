from django import forms
from .models import Cliente, Vehiculo

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['telefono', 'direccion']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +34 600 000 000'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingresa tu dirección completa'}),
        }
        labels = {
            'telefono': '📱 Teléfono',
            'direccion': '📍 Dirección',
        }

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        # Incluye todos los campos editables
        fields = ['marca', 'modelo', 'matricula', 'tipo', 'color']
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Toyota'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corolla'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1234XYZ'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Selecciona tipo'),
                ('Turismo', 'Turismo'),
                ('Motocicleta', 'Motocicleta'),
                ('Furgoneta', 'Furgoneta'),
                ('Otro', 'Otro'),
            ]),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Blanco'}),
        }
        labels = {
            'marca': '🚗 Marca',
            'modelo': '🚙 Modelo',
            'matricula': '🔢 Matrícula',
            'tipo': '⚙️ Tipo',
            'color': '🎨 Color',
        }