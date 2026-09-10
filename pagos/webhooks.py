import stripe
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Pago
from .services import StripeService

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    """Maneja eventos de Stripe."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return HttpResponseBadRequest("Payload inválido")
    except stripe.error.SignatureVerificationError:
        return HttpResponseBadRequest("Firma inválida")

    if event['type'] == 'payment_intent.succeeded':
        _manejar_exitoso(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        _manejar_fallido(event['data']['object'])
    elif event['type'] == 'payment_intent.processing':
        _manejar_procesando(event['data']['object'])

    return HttpResponse(status=200)


def _manejar_exitoso(intent):
    pago_id = intent['metadata'].get('pago_id')
    try:
        pago = Pago.objects.get(pk=pago_id)
        if pago.estado != 'completado':
            pago.estado = 'completado'
            pago.metodo_pago = StripeService.detectar_metodo_pago(intent)
            pago.save()
            pago.reserva.estado = 'confirmada'
            pago.reserva.save()
    except Pago.DoesNotExist:
        pass


def _manejar_fallido(intent):
    pago_id = intent['metadata'].get('pago_id')
    try:
        pago = Pago.objects.get(pk=pago_id)
        pago.estado = 'fallido'
        pago.stripe_error_message = intent.get('last_payment_error', {}).get('message')
        pago.save()
    except Pago.DoesNotExist:
        pass


def _manejar_procesando(intent):
    pago_id = intent['metadata'].get('pago_id')
    try:
        pago = Pago.objects.get(pk=pago_id)
        if pago.estado != 'completado':
            pago.estado = 'procesando'
            pago.save()
    except Pago.DoesNotExist:
        pass