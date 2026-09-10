# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction
from .models import Plaza, Reserva, Plazo
from .forms import ReservaForm, PlazaForm
from clientes.decorators import establecimiento_required
from django.http import JsonResponse
from .models import Plaza, Plazo, Reserva
from django.db.models import Q
from datetime import datetime, timedelta

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

    # Estadísticas: reservas por plaza
    reservas_por_plaza = []
    for plaza in plazas:
        count = Reserva.objects.filter(
            plazo__plaza=plaza,
            estado__in=['confirmada', 'completada']
        ).count()
        reservas_por_plaza.append({'numero': plaza.numero, 'nivel': plaza.nivel, 'count': count})

    # Estadísticas: reservas por día (últimos 30 días)
    reservas_por_dia = []
    for i in range(29, -1, -1):
        dia = hoy - timedelta(days=i)
        count = Reserva.objects.filter(
            plazo__fecha_inicio__lte=dia,
            plazo__fecha_fin__gte=dia,
            estado__in=['confirmada', 'completada']
        ).count()
        reservas_por_dia.append({'fecha': dia.strftime('%d/%m'), 'count': count})

    # Reservas por nivel
    reservas_por_nivel = {}
    for nivel in ['Sótano 1', 'Sótano 2', 'Planta 0']:
        count = Reserva.objects.filter(
            plazo__plaza__nivel=nivel,
            estado__in=['confirmada', 'completada']
        ).count()
        reservas_por_nivel[nivel] = count

    context = {
        'plazas': plazas,
        'libres_count': libres_count,
        'ocupadas_count': ocupadas_count,
        'total_count': total_count,
        'reservas_por_plaza': reservas_por_plaza,
        'reservas_por_dia': reservas_por_dia,
        'reservas_por_nivel': reservas_por_nivel,
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

# Vista para listar plazas disponibles
def listar_plazas(request):
    plazos = Plazo.objects.filter(disponible=True).select_related('plaza').order_by('plaza__nivel', 'plaza__numero', 'fecha_inicio')
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

    # Limpiar reservas pendientes expiradas (> 5 minutos)
    ahora = timezone.now()
    expiradas = Reserva.objects.filter(estado='pendiente', fecha_creacion__lt=ahora - timedelta(minutes=5))
    for exp in expiradas:
        if exp.plazo:
            exp.plazo.disponible = True
            exp.plazo.save()
        exp.estado = 'cancelada'
        exp.save()

    plazo = None
    if plazo_id:
        plazo = Plazo.objects.filter(id=plazo_id).first()

    if request.method == 'POST':
        form = ReservaForm(request.POST, user=request.user)
        plazos_rango_ids = request.POST.getlist("plazos_rango")

        if not plazos_rango_ids:
            single_p = request.POST.get("plazo")
            if single_p:
                plazos_rango_ids = [single_p]

        if form.is_valid() or plazos_rango_ids:
            selected_vehiculo = form.cleaned_data.get("vehiculo")
            if not selected_vehiculo and request.POST.get("vehiculo"):
                try:
                    selected_vehiculo = Vehiculo.objects.get(pk=request.POST.get("vehiculo"), cliente=cliente)
                except Exception:
                    pass

            ids_a_reservar = [int(pid) for pid in plazos_rango_ids if pid.isdigit()]
            if not ids_a_reservar and form.cleaned_data.get("plazo"):
                ids_a_reservar = [form.cleaned_data["plazo"].pk]
            elif not ids_a_reservar and plazo:
                ids_a_reservar = [plazo.pk]

            if not ids_a_reservar or not selected_vehiculo:
                messages.error(request, "Debes seleccionar un vehículo y un rango de fechas válido.")
                return redirect("mapa_plazas")

            try:
                with transaction.atomic():
                    plazos_bloqueados = list(
                        Plazo.objects
                        .select_for_update()
                        .select_related("plaza")
                        .filter(pk__in=ids_a_reservar)
                    )

                    if len(plazos_bloqueados) != len(ids_a_reservar):
                        raise ValueError("Algunos de los plazos seleccionados ya no existen.")

                    for p_bloq in plazos_bloqueados:
                        if not p_bloq.plaza.activo:
                            raise ValueError("Una de las plazas seleccionadas no está activa.")

                        existe_reserva_activa = Reserva.objects.filter(
                            plazo=p_bloq,
                            estado__in=["confirmada"],
                        ).exists()

                        if not p_bloq.disponible or existe_reserva_activa:
                            raise ValueError(f"El día {p_bloq.fecha_inicio} ya ha sido reservado por otro usuario.")

                    for p_bloq in plazos_bloqueados:
                        p_bloq.disponible = False
                        p_bloq.save(update_fields=["disponible"])

                    # Crear una sola reserva con el rango completo
                    primer_plazo = plazos_bloqueados[0]
                    ultimo_plazo = plazos_bloqueados[-1]
                    precio_total = sum(p.precio for p in plazos_bloqueados)
                    
                    reserva = Reserva.objects.create(
                        cliente=cliente,
                        vehiculo=selected_vehiculo,
                        plazo=primer_plazo,
                        fecha_fin=ultimo_plazo.fecha_fin,
                        estado="pendiente",
                    )

                messages.success(request, "¡Reserva creada! Ahora procede al pago.")
                return redirect("calcular_precio_y_pagar", reserva_id=reserva.pk)

            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect("mapa_plazas")
            except Exception as e:
                messages.error(request, f"Error al guardar la reserva: {e}")
                return redirect("mapa_plazas")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            return redirect("mapa_plazas")
    else:
        initial_data = {}
        if plazo:
            initial_data['plazo'] = plazo
        form = ReservaForm(initial=initial_data, user=request.user)
        if plazo:
            # Poner en trámite/pendiente por 5 minutos al iniciar el proceso de reserva
            try:
                plazo.disponible = False
                plazo.save()
                Reserva.objects.create(
                    cliente=cliente,
                    plazo=plazo,
                    estado='pendiente'
                )
            except Exception:
                pass

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

@establecimiento_required
def gestionar_reservas(request):
    reservas = Reserva.objects.select_related('plazo__plaza', 'cliente', 'vehiculo', 'pago').order_by('-fecha_creacion')
    
    confirmadas = reservas.filter(estado='confirmada').count()
    pendientes = reservas.filter(estado='pendiente').count()
    canceladas = reservas.filter(estado='cancelada').count()
    completadas = reservas.filter(estado='completada').count()
    
    context = {
        'reservas': reservas,
        'total_count': reservas.count(),
        'confirmadas_count': confirmadas,
        'pendientes_count': pendientes,
        'canceladas_count': canceladas,
        'completadas_count': completadas,
    }
    return render(request, 'core/gestionar_reservas.html', context)

#Vista para mostrar mapa interactivo de las plazas
# core/views.py



def mapa_plazas(request):
    """
    Vista del mapa interactivo con planos reales y filtrado preciso por día.
    """
    nivel = request.GET.get('nivel', 'Sótano 1')
    fecha_str = request.GET.get('fecha', '')
    
    filtro_fecha = None
    if fecha_str:
        try:
            filtro_fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    niveles = ['Sótano 1', 'Sótano 2', 'Planta 0']
    plazas_todas = Plaza.objects.all()
    
    plazas_con_estado = []
    
    for plaza in plazas_todas:
        hoy = datetime.now().date()
        
        # 1. Obtener plazos para la fecha seleccionada o por defecto (usando fecha_inicio / fecha_fin)
        if filtro_fecha:
            plazos_disponibles_qs = Plazo.objects.filter(plaza=plaza, fecha_inicio__lte=filtro_fecha, fecha_fin__gte=filtro_fecha, disponible=True)
            plazos_todos_qs = Plazo.objects.filter(plaza=plaza, fecha_inicio__lte=filtro_fecha, fecha_fin__gte=filtro_fecha)
        else:
            plazos_disponibles_qs = Plazo.objects.filter(plaza=plaza, fecha_fin__gte=hoy, disponible=True)
            plazos_todos_qs = Plazo.objects.filter(plaza=plaza, fecha_fin__gte=hoy)

        # 2. Comprobar reservas confirmadas o en trámite para ese día/plazos
        if filtro_fecha:
            tiene_reserva = Reserva.objects.filter(
                plazo__plaza=plaza,
                plazo__fecha_inicio__lte=filtro_fecha,
                plazo__fecha_fin__gte=filtro_fecha,
                estado__in=['confirmada', 'pendiente']
            ).exists()
        else:
            # Si no hay fecha seleccionada, la plaza está libre si tiene al menos un plazo disponible a futuro
            tiene_reserva = not plazos_disponibles_qs.exists()

        # 3. Determinar el estado exacto de la plaza
        if not plazos_todos_qs.exists():
            estado = 'ocupada'
        elif tiene_reserva:
            estado = 'ocupada'
        else:
            estado = 'libre'

        precio = plazos_todos_qs.first().precio if plazos_todos_qs.exists() else 0.00
        
        plazas_con_estado.append({
            'id': plaza.id,
            'numero': plaza.numero,
            'nivel': plaza.nivel.strip(),
            'pixel_x': plaza.pixel_x,
            'pixel_y': plaza.pixel_y,
            'radio': plaza.radio,
            'estado': estado,
            'precio': float(precio),
            'plazos_disponibles': plazos_disponibles_qs.count(),
        })
    
    imagen_width = 1754
    imagen_height = 1240
    
    contexto = {
        'plazas': plazas_con_estado,
        'niveles': niveles,
        'nivel_actual': nivel,
        'fecha_actual': fecha_str,
        'imagen_width': imagen_width,
        'imagen_height': imagen_height,
    }
    
    return render(request, 'core/mapa_plazas.html', contexto)


def obtener_plazos_plaza(request, plaza_id):
    """
    API AJAX para obtener los plazos disponibles y vehículos del usuario.
    """
    plaza = get_object_or_404(Plaza, id=plaza_id)
    
    hoy = datetime.now().date()
    plazos_qs = Plazo.objects.filter(
        plaza=plaza,
        fecha_fin__gte=hoy,
        disponible=True
    ).values('id', 'fecha_inicio', 'fecha_fin', 'precio')
    
    plazos = []
    for p in plazos_qs:
        plazos.append({
            'id': p['id'],
            'fecha': p['fecha_inicio'].isoformat(),
            'horario_desde': f"Del {p['fecha_inicio']} al {p['fecha_fin']}",
            'horario_hasta': '',
            'precio': float(p['precio'])
        })

    vehiculos = []
    if request.user.is_authenticated and hasattr(request.user, 'cliente_perfil'):
        vehiculos = list(request.user.cliente_perfil.vehiculos.values('id', 'marca', 'modelo', 'matricula'))

    return JsonResponse({
        'plaza': plaza.numero,
        'nivel': plaza.nivel,
        'plazos': plazos,
        'vehiculos': vehiculos
    })
    

