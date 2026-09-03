# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Plaza, Reserva, Plazo
from .forms import ReservaForm, PlazaForm
from clientes.decorators import establecimiento_required

@establecimiento_required
def gestionar_plazas(request):
    plazas = Plaza.objects.all().order_by('numero')
    libres_count = plazas.filter(ocupada=False).count()
    ocupadas_count = plazas.filter(ocupada=True).count()
    total_count = plazas.count()
    
    context = {
        'plazas': plazas,
        'libres_count': libres_count,
        'ocupadas_count': ocupadas_count,
        'total_count': total_count,
    }
    return render(request, 'core/gestionar_plazas.html', context)

@establecimiento_required
def crear_plaza_admin(request):
    if request.method == 'POST':
        form = PlazaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Plaza creada correctamente!')
            return redirect('gestionar_plazas')
    else:
        form = PlazaForm()
    
    return render(request, 'core/gestionar_plazas_crear.html', {'form': form})
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
def crear_reserva(request, plazo_id=None):
    try:
        cliente = request.user.cliente_perfil
    except Exception:
        messages.error(request, 'Debes crear un perfil de cliente primero para poder reservar.')
        return redirect('crear_cliente')

    # Verificar si el cliente tiene vehículos registrados
    if not cliente.vehiculos.exists():
        messages.warning(request, 'Debes registrar al menos un vehículo antes de realizar una reserva.')
        return redirect('nuevo_vehiculo')

    plazo = None
    if plazo_id:
        plazo = get_object_or_404(Plazo, id=plazo_id, disponible=True)

    if request.method == 'POST':
        form = ReservaForm(request.POST, user=request.user)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = cliente
            if plazo:
                reserva.plaza = plazo.plaza
                reserva.dia = plazo.fecha
            try:
                reserva.save()
                if plazo:
                    plazo.disponible = False
                    plazo.save()
                messages.success(request, '¡Reserva creada con éxito!')
                return redirect('mis_reservas')
            except Exception as e:
                messages.error(request, f"Error al guardar la reserva: {e}")
        else:
            # Mostrar errores específicos del formulario por pantalla si los hay
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        initial_data = {}
        if plazo:
            initial_data = {'plaza': plazo.plaza, 'dia': plazo.fecha}
        form = ReservaForm(initial=initial_data, user=request.user)
    
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

#Vista para mostrar mapa interactivo de las plazas
# core/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Plaza, Plazo, Reserva
from django.db.models import Q
from datetime import datetime, timedelta

def mapa_plazas(request):
    """
    Vista del mapa interactivo con planos reales.
    """
    nivel = request.GET.get('nivel', 'Sótano 1')
    
    # Obtener todos los niveles disponibles
    niveles = Plaza.objects.values_list('nivel', flat=True).distinct().order_by('nivel')
    
    # Obtener plazas del nivel seleccionado
    plazas = Plaza.objects.filter(nivel=nivel)
    
    # Procesar estado de cada plaza
    plazas_con_estado = []
    
    for plaza in plazas:
        # Obtener plazos disponibles (próximos 7 días)
        hoy = datetime.now().date()
        plazos_futuros = Plazo.objects.filter(
            plaza=plaza,
            fecha__gte=hoy,
            fecha__lt=hoy + timedelta(days=7)
        )
        
        # Contar reservas activas
        reservas_confirmadas = Reserva.objects.filter(
            plazo__plaza=plaza,
            estado='confirmada',
            plazo__fecha__gte=hoy
        ).count()
        
        reservas_pendientes = Reserva.objects.filter(
            plazo__plaza=plaza,
            estado='pendiente',
            plazo__fecha__gte=hoy
        ).count()
        
        # Determinar estado
        if reservas_pendientes > 0:
            estado = 'tramite'  # Azul
        elif reservas_confirmadas > 0:
            estado = 'ocupada'  # Rojo
        else:
            estado = 'libre'  # Verde
        
        # Obtener el precio del primer plazo disponible
        precio = plazos_futuros.first().precio if plazos_futuros.exists() else 0.00
        
        plazas_con_estado.append({
            'id': plaza.id,
            'numero': plaza.numero,
            'nivel': plaza.nivel,
            'pixel_x': plaza.pixel_x,
            'pixel_y': plaza.pixel_y,
            'radio': plaza.radio,
            'estado': estado,
            'precio': float(precio),
            'plazos_disponibles': plazos_futuros.count(),
        })
    
    # Dimensiones de la imagen (ajusta según tu plano real)
    imagen_width = 1200  # Ancho de la imagen en píxeles
    imagen_height = 800  # Alto de la imagen en píxeles
    
    contexto = {
        'plazas': plazas_con_estado,
        'niveles': niveles,
        'nivel_actual': nivel,
        'imagen_width': imagen_width,
        'imagen_height': imagen_height,
    }
    
    return render(request, 'core/mapa_plazas.html', contexto)


def obtener_plazos_plaza(request, plaza_id):
    """
    API AJAX para obtener los plazos disponibles de una plaza específica.
    """
    plaza = get_object_or_404(Plaza, id=plaza_id)
    
    hoy = datetime.now().date()
    plazos = Plazo.objects.filter(
        plaza=plaza,
        fecha__gte=hoy,
        fecha__lt=hoy + timedelta(days=7),
        disponible=True
    ).values('id', 'fecha', 'horario_desde', 'horario_hasta', 'precio')
    
    return JsonResponse({
        'plaza': plaza.numero,
        'nivel': plaza.nivel,
        'plazos': list(plazos)
    })
    

