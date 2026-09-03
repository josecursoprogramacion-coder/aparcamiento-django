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
    plazas = Plaza.objects.all().order_by('nivel', 'numero')
    
    # Calcular libres y ocupadas basadas en si tienen plazos ocupados o reservas
    hoy = datetime.now().date()
    ocupadas_ids = Reserva.objects.filter(estado='confirmada').values_list('plazo__plaza_id', flat=True)
    
    libres_count = plazas.exclude(id__in=ocupadas_ids).count()
    ocupadas_count = plazas.filter(id__in=ocupadas_ids).count()
    total_count = plazas.count()
    
    for plaza in plazas:
        plaza.is_ocupada = plaza.id in ocupadas_ids

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
        reservas = Reserva.objects.filter(cliente=cliente).exclude(estado='cancelada')
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

    plazo = None
    if plazo_id:
        plazo = get_object_or_404(Plazo, id=plazo_id, disponible=True)

    if request.method == 'POST':
        form = ReservaForm(request.POST, user=request.user)
        if form.is_valid():
            selected_plazo = form.cleaned_data['plazo']
            selected_vehiculo = form.cleaned_data['vehiculo']
            try:
                reserva = Reserva.objects.create(
                    cliente=cliente,
                    vehiculo=selected_vehiculo,
                    plazo=selected_plazo,
                    estado='confirmada'
                )
                selected_plazo.disponible = False
                selected_plazo.save()
                messages.success(request, '¡Reserva creada con éxito!')
                return redirect('mis_reservas')
            except Exception as e:
                messages.error(request, f"Error al guardar la reserva: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = ReservaForm(initial={'plazo': plazo} if plazo else None, user=request.user)

    return render(request, 'core/crear_reserva.html', {'form': form, 'plazo': plazo})

@login_required
def cancelar_reserva_cliente(request, pk):
    try:
        cliente = request.user.cliente_perfil
    except Exception:
        messages.error(request, 'No tienes un perfil de cliente asociado.')
        return redirect('mis_reservas')

    reserva = get_object_or_404(Reserva, pk=pk, cliente=cliente)
    reserva.cancelar()
    messages.success(request, '¡Tu reserva ha sido cancelada y la plaza liberada con éxito!')
    return redirect('mis_reservas')
@establecimiento_required
def cancelar_reserva_admin(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.cancelar()  # Asegúrate de que este método exista en el modelo
    messages.success(request, 'Reserva cancelada y plaza liberada.')
    return redirect('listar_reservas_admin')

# Vista para listar todas las reservas (solo establecimientos)
@establecimiento_required
def listar_reservas_admin(request):
    reservas = Reserva.objects.exclude(estado='cancelada').order_by('-fecha_creacion')
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
    
    # Obtener todos los niveles disponibles ordenados explícitamente
    niveles = ['Sótano 1', 'Sótano 2', 'Planta 0']
    
    # Obtener TODAS las plazas de todos los niveles para pasarlas a JavaScript (plazasData)
    plazas_todas = Plaza.objects.all()
    
    plazas_con_estado = []
    
    for plaza in plazas_todas:
        hoy = datetime.now().date()
        plazos_futuros = Plazo.objects.filter(
            plaza=plaza,
            fecha__gte=hoy,
            fecha__lt=hoy + timedelta(days=7)
        )
        
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
        
        if reservas_pendientes > 0:
            estado = 'tramite'
        elif reservas_confirmadas > 0:
            estado = 'ocupada'
        else:
            estado = 'libre'
        
        precio = plazos_futuros.first().precio if plazos_futuros.exists() else 0.00
        
        plazas_con_estado.append({
            'id': plaza.id,
            'numero': plaza.numero,
            'nivel': plaza.nivel.strip(),
            'pixel_x': plaza.pixel_x,
            'pixel_y': plaza.pixel_y,
            'radio': plaza.radio,
            'estado': estado,
            'precio': float(precio),
            'plazos_disponibles': plazos_futuros.count(),
        })
    
    imagen_width = 1754
    imagen_height = 1240
    
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
    

