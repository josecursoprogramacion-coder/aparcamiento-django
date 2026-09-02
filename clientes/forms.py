from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, Vehiculo

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
        label='📧 Correo Electrónico'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'email':
                field.widget.attrs.update({'class': 'form-control'})

class EditarUsuarioForm(forms.ModelForm):
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='👤 Nombre')
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='👤 Apellidos')
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}), label='📧 Correo Electrónico')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

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
                ('normal', 'Normal'),
                ('premium', 'Premium'),
                ('electrico', 'Eléctrico'),
                ('turismo', 'Turismo'),
                ('motocicleta', 'Motocicleta'),
                ('furgoneta', 'Furgoneta'),
                ('otro', 'Otro'),
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