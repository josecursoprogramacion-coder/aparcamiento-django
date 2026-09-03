# core/views.py

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from clientes.decorators import establecimiento_required

from .forms import PlazaForm, ReservaForm
from .models import Plaza, Plazo, Reserva


# ---------------------------------------------------------------------------
# MAPA REAL DEL PARKING
# ---------------------------------------------------------------------------
# Los tres JPG tienen exactamente 1754 x 1240 px.
#
# Cada tupla contiene:
#     numero: (pixel_x, pixel_y)
#
# Las posiciones corresponden al centro de los rectángulos que el usuario
# numeró en planta0.jpg, sotano1.jpg y sotano2.jpg.
#
# Solo estas 30 plazas son seleccionables.
# ---------------------------------------------------------------------------

IMAGEN_WIDTH = 1754
IMAGEN_HEIGHT = 1240

NIVELES = [
    Plaza.PLANTA_0,
    Plaza.SOTANO_1,
    Plaza.SOTANO_2,
]

MAPA_PLAZAS = {
    Plaza.PLANTA_0: {
        1: (425, 763),
        2: (427, 820),
        3: (587, 849),
        4: (970, 691),
        5: (976, 794),
        6: (889, 382),
        7: (734, 1014),
        8: (606, 706),
        9: (600, 1013),
        10: (764, 402),
    },
    Plaza.SOTANO_1: {
        1: (1230, 579),
        2: (1368, 477),
        3: (1136, 299),
        4: (889, 382),
        5: (586, 813),
        6: (698, 838),
        7: (518, 552),
        8: (980, 792),
        9: (733, 1008),
        10: (417, 867),
    },
    Plaza.SOTANO_2: {
        1: (1205, 545),
        2: (1054, 319),
        3: (982, 745),
        4: (691, 836),
        5: (621, 695),
        6: (729, 417),
        7: (694, 993),
        8: (975, 1010),
        9: (425, 814),
        10: (401, 735),
    },
}


def _sincronizar_plazas_del_mapa():
    """
    Garantiza que las 30 plazas del mapa existan en BD y tengan siempre las
    coordenadas correctas.

    No elimina filas antiguas para no destruir reservas históricas. Las plazas
    fuera de este mapa quedan desactivadas y no aparecen en la interfaz.
    """
    claves_validas = []

    for nivel, plazas in MAPA_PLAZAS.items():
        for numero, (pixel_x, pixel_y) in plazas.items():
            plaza, _ = Plaza.objects.update_or_create(
                nivel=nivel,
                numero=numero,
                defaults={
                    "pixel_x": pixel_x,
                    "pixel_y": pixel_y,
                    "radio": 28,
                    "activo": True,
                },
            )
            claves_validas.append(plaza.pk)

    Plaza.objects.exclude(pk__in=claves_validas).update(activo=False)


def _limpiar_reservas_pendientes_expiradas():
    """
    Libera reservas pendientes cuya ventana temporal ya ha expirado.
    Es compatible con reservas antiguas del flujo anterior.
    """
    ahora = timezone.now()

    expiradas = Reserva.objects.select_related("plazo").filter(
        estado="pendiente",
        expira_en__isnull=False,
        expira_en__lt=ahora,
    )

    for reserva in expiradas:
        plazo = reserva.plazo
        reserva.estado = "cancelada"
        reserva.save(update_fields=["estado"])

        if plazo:
            sigue_ocupado = Reserva.objects.filter(
                plazo=plazo,
                estado__in=["pendiente", "confirmada"],
            ).exists()

            if not sigue_ocupado:
                plazo.disponible = True
                plazo.save(update_fields=["disponible"])


def _ids_plazos_bloqueados():
    """
    IDs de plazos que no pueden volver a reservarse.
    """
    ahora = timezone.now()

    return Reserva.objects.filter(
        estado__in=["pendiente", "confirmada"],
    ).filter(
        # Una confirmada siempre bloquea.
        # Una pendiente solo bloquea mientras no haya expirado.
        # Las pendientes antiguas sin expira_en se mantienen por compatibilidad.
        models_q_confirmada_o_pendiente_vigente(ahora)
    ).values_list("plazo_id", flat=True)


def models_q_confirmada_o_pendiente_vigente(ahora):
    """
    Helper separado para mantener legible la consulta.
    Importamos Q de forma local para no ensuciar los imports generales.
    """
    from django.db.models import Q

    return (
        Q(estado="confirmada")
        | Q(estado="pendiente", expira_en__isnull=True)
        | Q(estado="pendiente", expira_en__gt=ahora)
    )


# ---------------------------------------------------------------------------
# ADMINISTRACIÓN DE PLAZAS
# ---------------------------------------------------------------------------

@establecimiento_required
def gestionar_plazas(request):
    _sincronizar_plazas_del_mapa()
    _limpiar_reservas_pendientes_expiradas()

    plazas = Plaza.objects.filter(activo=True).order_by("nivel", "numero")

    ocupadas_ids = Reserva.objects.filter(
        estado="confirmada",
        plazo__isnull=False,
    ).values_list("plazo__plaza_id", flat=True)

    ocupadas_set = set(ocupadas_ids)

    for plaza in plazas:
        plaza.is_ocupada = plaza.pk in ocupadas_set

    context = {
        "plazas": plazas,
        "libres_count": sum(not p.is_ocupada for p in plazas),
        "ocupadas_count": sum(p.is_ocupada for p in plazas),
        "total_count": plazas.count(),
    }

    return render(request, "core/gestionar_plazas.html", context)


@establecimiento_required
def crear_plaza_admin(request):
    """
    Se conserva por compatibilidad con la zona de administración.

    El mapa público únicamente mostrará las plazas 1-10 de las tres plantas
    definidas en MAPA_PLAZAS.
    """
    if request.method == "POST":
        form = PlazaForm(request.POST)

        if form.is_valid():
            plaza = form.save(commit=False)

            if plaza.nivel not in MAPA_PLAZAS:
                messages.error(request, "Ese nivel no forma parte del parking.")
            elif plaza.numero not in MAPA_PLAZAS[plaza.nivel]:
                messages.error(
                    request,
                    "Solo existen las plazas numeradas del 1 al 10.",
                )
            else:
                x, y = MAPA_PLAZAS[plaza.nivel][plaza.numero]
                plaza.pixel_x = x
                plaza.pixel_y = y
                plaza.radio = 28
                plaza.activo = True
                plaza.save()

                messages.success(request, "¡Plaza creada correctamente!")
                return redirect("gestionar_plazas")
    else:
        form = PlazaForm()

    return render(
        request,
        "core/gestionar_plazas_crear.html",
        {"form": form},
    )


# ---------------------------------------------------------------------------
# LISTADOS Y RESERVAS
# ---------------------------------------------------------------------------

def listar_plazas(request):
    _sincronizar_plazas_del_mapa()
    _limpiar_reservas_pendientes_expiradas()

    bloqueados = _ids_plazos_bloqueados()

    plazos = (
        Plazo.objects
        .filter(
            plaza__activo=True,
            disponible=True,
            fecha__gte=timezone.localdate(),
        )
        .exclude(pk__in=bloqueados)
        .select_related("plaza")
        .order_by("fecha", "horario_desde")
    )

    return render(
        request,
        "core/listar_plazas.html",
        {"plazos": plazos},
    )


@login_required
def mis_reservas(request):
    try:
        cliente = request.user.cliente_perfil
    except Exception:
        reservas = Reserva.objects.none()
    else:
        reservas = (
            Reserva.objects
            .filter(cliente=cliente)
            .exclude(estado="cancelada")
            .select_related("plazo", "plazo__plaza", "vehiculo")
        )

    return render(
        request,
        "core/mis_reservas.html",
        {"reservas": reservas},
    )


@login_required
def crear_reserva(request, plazo_id=None):
    """
    Crea la reserva únicamente al enviar el formulario.

    A diferencia del código anterior, abrir esta pantalla NO marca el plazo
    como ocupado. La comprobación definitiva se realiza dentro de una
    transacción y con select_for_update(), evitando dobles reservas por carrera.
    """
    _sincronizar_plazas_del_mapa()
    _limpiar_reservas_pendientes_expiradas()

    try:
        cliente = request.user.cliente_perfil
    except Exception:
        messages.error(
            request,
            "Debes crear un perfil de cliente primero para poder reservar.",
        )
        return redirect("crear_cliente")

    plazo = None

    if plazo_id is not None:
        plazo = get_object_or_404(
            Plazo.objects.select_related("plaza"),
            pk=plazo_id,
            plaza__activo=True,
        )

        if not plazo.disponible:
            messages.error(request, "Ese horario ya no está disponible.")
            return redirect("mapa_plazas")

    if request.method == "POST":
        form = ReservaForm(request.POST, user=request.user)
        plazos_rango_ids = request.POST.getlist("plazos_rango")

        if form.is_valid():
            selected_vehiculo = form.cleaned_data["vehiculo"]
            
            ids_a_reservar = [int(pid) for pid in plazos_rango_ids if pid.isdigit()]
            if not ids_a_reservar and form.cleaned_data.get("plazo"):
                ids_a_reservar = [form.cleaned_data["plazo"].pk]

            if not ids_a_reservar:
                messages.error(request, "Debes seleccionar un rango de fechas válido.")
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
                            estado__in=["pendiente", "confirmada"],
                        ).filter(
                            models_q_confirmada_o_pendiente_vigente(timezone.now())
                        ).exists()

                        if not p_bloq.disponible or existe_reserva_activa:
                            raise ValueError(f"El día {p_bloq.fecha} ya ha sido reservado por otro usuario.")

                    for p_bloq in plazos_bloqueados:
                        Reserva.objects.create(
                            cliente=cliente,
                            vehiculo=selected_vehiculo,
                            plazo=p_bloq,
                            estado="confirmada",
                            expira_en=None,
                        )
                        p_bloq.disponible = False
                        p_bloq.save(update_fields=["disponible"])

                messages.success(request, "¡Reserva creada con éxito para todo el rango seleccionado!")
                return redirect("mis_reservas")

            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect("mapa_plazas")
            except Exception as e:
                messages.error(request, f"Error al guardar la reserva: {e}")
                return redirect("mapa_plazas")
    else:
        form = ReservaForm(
            initial={"plazo": plazo} if plazo else None,
            user=request.user,
        )

    return render(
        request,
        "core/crear_reserva.html",
        {
            "form": form,
            "plazo": plazo,
        },
    )


@login_required
def cancelar_reserva_cliente(request, pk):
    try:
        cliente = request.user.cliente_perfil
    except Exception:
        messages.error(
            request,
            "No tienes un perfil de cliente asociado.",
        )
        return redirect("mis_reservas")

    reserva = get_object_or_404(
        Reserva,
        pk=pk,
        cliente=cliente,
    )

    reserva.cancelar()

    messages.success(
        request,
        "¡Tu reserva ha sido cancelada y la plaza liberada con éxito!",
    )
    return redirect("mis_reservas")


@establecimiento_required
def cancelar_reserva_admin(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.cancelar()

    messages.success(
        request,
        "Reserva cancelada y plaza liberada.",
    )
    return redirect("listar_reservas_admin")


@establecimiento_required
def listar_reservas_admin(request):
    reservas = (
        Reserva.objects
        .exclude(estado="cancelada")
        .select_related("cliente", "vehiculo", "plazo", "plazo__plaza")
        .order_by("-fecha_creacion")
    )

    return render(
        request,
        "core/listar_reservas_admin.html",
        {"reservas": reservas},
    )


# ---------------------------------------------------------------------------
# MAPA INTERACTIVO
# ---------------------------------------------------------------------------

def mapa_plazas(request):
    """
    Mapa interactivo de las 30 plazas reales:
        - Planta 0: 1-10
        - Sótano 1: 1-10
        - Sótano 2: 1-10
    """
    _sincronizar_plazas_del_mapa()
    _limpiar_reservas_pendientes_expiradas()

    nivel = request.GET.get("nivel", Plaza.PLANTA_0)

    if nivel not in NIVELES:
        nivel = Plaza.PLANTA_0

    hoy = timezone.localdate()
    limite = hoy + timedelta(days=7)

    plazas = (
        Plaza.objects
        .filter(
            activo=True,
            nivel__in=NIVELES,
            numero__gte=1,
            numero__lte=10,
        )
        .order_by("nivel", "numero")
    )

    plazas_con_estado = []

    for plaza in plazas:
        plazos_futuros = PlazaPlazosQuery(plaza, hoy, limite)

        total_plazos = plazos_futuros.total()
        disponibles = plazos_futuros.disponibles()

        pendientes = Reserva.objects.filter(
            plazo__plaza=plaza,
            estado="pendiente",
            plazo__fecha__gte=hoy,
            plazo__fecha__lt=limite,
        ).filter(
            models_q_confirmada_o_pendiente_vigente(timezone.now())
        ).exists()

        if disponibles.exists():
            estado = "libre"
        elif pendientes:
            estado = "tramite"
        elif total_plazos > 0:
            estado = "ocupada"
        else:
            estado = "sin_plazos"

        primer_disponible = disponibles.first()
        primer_plazo = primer_disponible or plazos_futuros.queryset.first()

        plazas_con_estado.append(
            {
                "id": plaza.pk,
                "numero": plaza.numero,
                "nivel": plaza.nivel,
                "pixel_x": plaza.pixel_x,
                "pixel_y": plaza.pixel_y,
                "radio": plaza.radio,
                "estado": estado,
                "precio": float(primer_plazo.precio) if primer_plazo else 0.0,
                "plazos_disponibles": disponibles.count(),
            }
        )

    contexto = {
        "plazas": plazas_con_estado,
        "niveles": NIVELES,
        "nivel_actual": nivel,
        "imagen_width": IMAGEN_WIDTH,
        "imagen_height": IMAGEN_HEIGHT,
    }

    return render(
        request,
        "core/mapa_plazas.html",
        contexto,
    )


class PlazaPlazosQuery:
    """
    Pequeño helper para reutilizar la consulta de plazos de una plaza.
    """

    def __init__(self, plaza, desde, hasta):
        self.queryset = Plazo.objects.filter(
            plaza=plaza,
            fecha__gte=desde,
            fecha__lt=hasta,
        ).order_by("fecha", "horario_desde")

    def total(self):
        return self.queryset.count()

    def disponibles(self):
        bloqueados = _ids_plazos_bloqueados()

        return self.queryset.filter(
            disponible=True,
        ).exclude(
            pk__in=bloqueados,
        )


def obtener_plazos_plaza(request, plaza_id):
    """
    Endpoint AJAX usado por el mapa.
    Devuelve únicamente horarios realmente reservables.
    """
    _limpiar_reservas_pendientes_expiradas()

    plaza = get_object_or_404(
        Plaza,
        pk=plaza_id,
        activo=True,
        nivel__in=NIVELES,
        numero__gte=1,
        numero__lte=10,
    )

    hoy = timezone.localdate()
    limite = hoy + timedelta(days=7)

    bloqueados = _ids_plazos_bloqueados()

    plazos = (
        Plazo.objects
        .filter(
            plaza=plaza,
            fecha__gte=hoy,
            fecha__lt=limite,
            disponible=True,
        )
        .exclude(pk__in=bloqueados)
        .order_by("fecha", "horario_desde")
        .values(
            "id",
            "fecha",
            "horario_desde",
            "horario_hasta",
            "precio",
        )
    )

    # JsonResponse no serializa bien Decimal/Time en todas las versiones
    # si convertimos el ValuesQuerySet directamente. Lo normalizamos.
    datos = [
        {
            "id": p["id"],
            "fecha": p["fecha"].isoformat(),
            "horario_desde": p["horario_desde"].strftime("%H:%M"),
            "horario_hasta": p["horario_hasta"].strftime("%H:%M"),
            "precio": float(p["precio"]),
        }
        for p in plazos
    ]

    vehiculos = []
    if request.user.is_authenticated and hasattr(request.user, "cliente_perfil"):
        vehiculos = list(
            request.user.cliente_perfil.vehiculos.values(
                "id", "marca", "modelo", "matricula"
            )
        )

    return JsonResponse(
        {
            "plaza": plaza.numero,
            "nivel": plaza.nivel,
            "plazos": datos,
            "vehiculos": vehiculos,
        }
    )
