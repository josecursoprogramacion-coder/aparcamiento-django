# core/views.py

from django.shortcuts import render, redirect, get_object_or_404  # ← CORREGIDO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Plaza, Reserva, Plazo
from .forms import ReservaForm
from clientes.models import Vehiculo
from clientes.decorators import establecimiento_required

# Vista para listar plazas disponibles
def listar_plazas(request):
    plazos = Plazo.objects.filter(disponible=True).order_by('fecha', 'horario_desde')
    return render(request, 'core/listar_plazas.html', {'plazos': plazos})

# Vista para ver mis reservas
@login_required
def mis_reservas(request):
    try:
        cliente = request.user.cliente_perfil
        reservas = Reserva.objects.filter(cliente=cliente)
    except Exception:
        reservas = []
    return render(request, 'core/mis_reservas.html', {'reservas': reservas})

# Vista para crear una reserva
@login_required
def crear_reserva(request, plazo_id):
    plazo = get_object_or_404(Plazo, id=plazo_id, disponible=True)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = request.user.cliente_perfil  # Asegúrate de que este perfil exista
            reserva.plazo = plazo
            reserva.save()
            messages.success(request, 'Reserva creada con éxito.')
            return redirect('mis_reservas')
    else:
        form = ReservaForm()
    
    return render(request, 'core/crear_reserva.html', {'form': form, 'plazo': plazo})

# Vista para cancelar una reserva (solo establecimientos)
@establecimiento_required
def cancelar_reserva_admin(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.cancelar()  # Asegúrate de que este método exista en el modelo
    messages.success(request, 'Reserva cancelada y plaza liberada.')
    return redirect('listar_reservas_admin')

# Vista para listar todas las reservas (solo establecimientos)
@establecimiento_required
def listar_reservas_admin(request):
    reservas = Reserva.objects.all().order_by('-dia')
    return render(request, 'core/listar_reservas_admin.html', {'reservas': reservas})
