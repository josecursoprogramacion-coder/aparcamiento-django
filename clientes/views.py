# clientes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Cliente, Reserva, Vehiculo
from core.models import Plazo
from django.contrib import messages
from .forms import ClienteForm, VehiculoForm, RegistroUsuarioForm, EditarUsuarioForm

def inicio(request):
    return render(request, 'clientes/inicio.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada con éxito!')
            return redirect('inicio')
    else:
        form = RegistroUsuarioForm()
    # Ruta CORRECTA (registro.html en la raíz)
    return render(request, 'registro.html', {'form': form})

@login_required
def mis_reservas(request):
    reservas = Reserva.objects.filter(cliente__usuario=request.user)
    # Ruta CORRECTA (core/mis_reservas.html)
    return render(request, 'core/mis_reservas.html', {'reservas': reservas})

def listar_plazas(request):
    plazos = Plazo.objects.filter(disponible=True).order_by('fecha', 'horario_desde')
    # Ruta CORRECTA (core/listar_plazas.html)
    return render(request, 'core/listar_plazas.html', {'plazos': plazos})

def listar_reservas_admin(request):
    reservas = Reserva.objects.all()
    return render(request, 'core/listar_reservas_admin.html', {'reservas': reservas})

def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.usuario = request.user
            cliente.save()
            messages.success(request, '¡Perfil de cliente creado exitosamente!')
            return redirect('mis_vehiculos')
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/crear_cliente.html', {'form': form})

@login_required
def editar_perfil(request):
    try:
        cliente, created = Cliente.objects.get_or_create(usuario=request.user)
    except Exception:
        cliente = None

    if request.method == 'POST':
        user_form = EditarUsuarioForm(request.POST, instance=request.user)
        cliente_form = ClienteForm(request.POST, instance=cliente) if cliente else None

        if user_form.is_valid() and (not cliente_form or cliente_form.is_valid()):
            user_form.save()
            if cliente_form:
                c = cliente_form.save(commit=False)
                c.usuario = request.user
                c.save()
            messages.success(request, '¡Tus datos de perfil han sido actualizados con éxito!')
            return redirect('editar_perfil')
    else:
        user_form = EditarUsuarioForm(instance=request.user)
        cliente_form = ClienteForm(instance=cliente) if cliente else None

    return render(request, 'clientes/editar_perfil.html', {
        'user_form': user_form,
        'cliente_form': cliente_form
    })

def mis_vehiculos(request):
    try:
        cliente = request.user.cliente_perfil
    except Cliente.DoesNotExist:
        messages.warning(request, 'Necesitas crear un perfil de cliente para ver tus vehículos.')
        return redirect('crear_cliente')
    
    vehiculos = cliente.vehiculos.all()
    
    context = {
        'vehiculos': vehiculos
    }
    return render(request, 'clientes/mis_vehiculos.html', context)

@login_required
def nuevo_vehiculo(request):
    try:
        cliente = request.user.cliente_perfil
    except Cliente.DoesNotExist:
        messages.error(request, 'Debes crear un perfil de cliente primero.')
        return redirect('crear_cliente')

    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.cliente = cliente
            vehiculo.save()
            messages.success(request, '¡Vehículo añadido con éxito!')
            return redirect('mis_vehiculos')
    else:
        form = VehiculoForm()
    return render(request, 'clientes/nuevo_vehiculo.html', {'form': form})



@login_required
def editar_vehiculo(request, pk):
    """
    Vista para editar un vehículo existente.
    Solo el dueño del vehículo puede editarlo.
    """
    try:
        cliente = request.user.cliente_perfil
    except Cliente.DoesNotExist:
        messages.error(request, 'Necesitas crear un perfil de cliente.')
        return redirect('crear_cliente')
    
    # Obtener el vehículo específico del usuario
    vehiculo = get_object_or_404(Vehiculo, pk=pk, cliente=cliente)
    
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Vehículo actualizado correctamente!')
            return redirect('mis_vehiculos')
    else:
        form = VehiculoForm(instance=vehiculo)
    
    return render(request, 'clientes/editar_vehiculo.html', {
        'form': form,
        'vehiculo': vehiculo,
        'titulo': 'Editar Vehículo'
    })


@login_required
def eliminar_vehiculo(request, pk):
    """
    Vista para eliminar un vehículo.
    Solo el dueño del vehículo puede eliminarlo.
    """
    try:
        cliente = request.user.cliente_perfil
    except Cliente.DoesNotExist:
        messages.error(request, 'Necesitas crear un perfil de cliente.')
        return redirect('crear_cliente')
    
    vehiculo = get_object_or_404(Vehiculo, pk=pk, cliente=cliente)
    
    if request.method == 'POST':
        vehiculo.delete()
        messages.success(request, '¡Vehículo eliminado correctamente!')
        return redirect('mis_vehiculos')
    
    return render(request, 'clientes/confirmar_eliminacion.html', {
        'vehiculo': vehiculo
    })
    
