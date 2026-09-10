from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings

from .models import Pago
from .services import StripeService
from core.models import Reserva, Plazo
from clientes.decorators import cliente_required


@login_required
@cliente_required
def calcular_precio_y_pagar(request, reserva_id):
    """Calcula el precio y prepara el pago."""
    reserva = get_object_or_404(Reserva, pk=reserva_id, cliente=request.user.cliente_perfil)
    
    # Calcular precio total para multi-día
    if reserva.fecha_fin and reserva.fecha_fin > reserva.plazo.fecha_inicio:
        plazos_rango = Plazo.objects.filter(
            plaza=reserva.plazo.plaza,
            fecha_inicio__gte=reserva.plazo.fecha_inicio,
            fecha_fin__lte=reserva.fecha_fin,
            disponible=False
        )
        monto = sum(p.precio for p in plazos_rango)
    else:
        monto = reserva.plazo.precio

    pago, created = Pago.objects.get_or_create(
        reserva=reserva,
        defaults={'usuario': request.user, 'monto': monto, 'moneda': 'EUR'}
    )

    if pago.estado == 'completado':
        messages.info(request, "Esta reserva ya está pagada.")
        return redirect('mis_reservas')

    return render(request, 'pagos/checkout.html', {'pago': pago, 'reserva': reserva})


@login_required
@cliente_required
@require_POST
def iniciar_pago(request, pago_id):
    """Crea el PaymentIntent y devuelve el client_secret."""
    pago = get_object_or_404(Pago, pk=pago_id, usuario=request.user)

    if pago.estado == 'completado':
        return JsonResponse({'error': 'Pago ya completado'}, status=400)

    try:
        payment_intent = StripeService.crear_payment_intent(pago)
        return JsonResponse({
            'client_secret': payment_intent.client_secret,
            'pago_id': pago.id,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@cliente_required
def pago_resultado(request, pago_id):
    """Página de resultado tras el pago."""
    pago = get_object_or_404(Pago, pk=pago_id, usuario=request.user)

    if pago.stripe_payment_intent_id:
        try:
            intent = StripeService.obtener_estado_pago(pago.stripe_payment_intent_id)
            if intent.status == 'succeeded':
                if pago.estado != 'completado':
                    pago.estado = 'completado'
                    pago.metodo_pago = StripeService.detectar_metodo_pago(intent)
                    pago.save()
                    pago.reserva.estado = 'confirmada'
                    pago.reserva.save()
                    messages.success(request, f"¡Pago de {pago.monto}€ realizado! Método: {pago.get_metodo_pago_display()}")
            elif intent.status == 'requires_action':
                messages.info(request, "Confirma el pago en tu app bancaria (Bizum).")
        except Exception as e:
            messages.error(request, f"Error al verificar: {str(e)}")

    return render(request, 'pagos/resultado.html', {'pago': pago})


@login_required
@cliente_required
def reembolsar_pago(request, pago_id):
    """Reembolso (solo Establecimiento o Admin)."""
    if not (request.user.is_superuser or request.user.groups.filter(name='Establecimiento').exists()):
        messages.error(request, "Acceso denegado.")
        return redirect('listar_reservas_admin')

    pago = get_object_or_404(Pago, pk=pago_id)
    if pago.estado != 'completado':
        messages.error(request, "Solo se pueden reembolsar pagos completados.")
        return redirect('listar_reservas_admin')

    try:
        monto_reembolsar = float(request.POST.get('monto', pago.monto))
        motivo = request.POST.get('motivo', 'requested_by_customer')

        if monto_reembolsar > pago.reembolsable:
            messages.error(request, f"Monto excesivo. Reembolsable: {pago.reembolsable}€")
            return redirect('listar_reservas_admin')

        refund = StripeService.reembolsar_pago(pago.stripe_payment_intent_id, int(monto_reembolsar * 100), motivo)
        StripeService.registrar_reembolso(pago, refund.id, monto_reembolsar, motivo, request.user)

        if monto_reembolsar >= pago.reembolsable:
            pago.estado = 'reembolsado'
            pago.reserva.estado = 'cancelada'
            pago.reserva.save()

        messages.success(request, f"Reembolso de {monto_reembolsar}€ realizado.")
    except Exception as e:
        messages.error(request, str(e))

    return redirect('gestionar_reservas')
