from django import forms
from .models import Reserva
from clientes.models import Vehiculo,Plaza

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['plaza', 'dia']
        widgets = {
            'plaza' : forms.Select(attrs={'class' : 'form-control'}),
            'dia' : forms.DateInput(attrs={'class' : 'form-control', 'type' : 'date'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Filtrado de plazas libres
        self.fields['plaza'].queryset = Plaza.objects.filter(ocupada=False)