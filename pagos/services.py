import stripe
from django.conf import settings
from .models import Pago, Reembolso

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    @staticmethod
    def crear_payment_intent(pago: Pago):
        """Crea un PaymentIntent que soporta Tarjeta + Bizum + Apple Pay."""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=pago.monto_en_centavos,
                currency=pago.moneda.lower(),
                metadata={
                    'pago_id': str(pago.id),
                    'reserva_id': str(pago.reserva.id),
                    'usuario': pago.usuario.username,
                    'plaza': str(pago.reserva.plazo.plaza.numero),
                },
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'always',
                },
                description=f"Reserva Plaza {pago.reserva.plazo.plaza.numero} - {pago.reserva.plazo.fecha_inicio}",
            )
            pago.stripe_payment_intent_id = payment_intent.id
            pago.estado = 'procesando'
            pago.save()
            return payment_intent
        except stripe.error.StripeError as e:
            raise Exception(f"Error al crear pago: {e.user_message}")

    @staticmethod
    def obtener_estado_pago(payment_intent_id: str):
        """Verifica el estado real en Stripe."""
        return stripe.PaymentIntent.retrieve(payment_intent_id)

    @staticmethod
    def detectar_metodo_pago(payment_intent):
        """Extrae el método de pago usado."""
        try:
            charge = payment_intent['charges']['data'][0]
            method_type = charge['payment_method_details']['type']
            mapping = {'card': 'card', 'bizum': 'bizum', 'apple_pay': 'apple_pay', 'google_pay': 'google_pay'}
            return mapping.get(method_type, 'card')
        except (KeyError, IndexError):
            return 'card'

    @staticmethod
    def reembolsar_pago(payment_intent_id: str, monto_centavos=None, motivo: str = 'requested_by_customer'):
        """
        Crea un reembolso total o parcial.
        monto_centavos = None → reembolso total
        """
        try:
            params = {'payment_intent': payment_intent_id}
            if monto_centavos is not None:
                params['amount'] = int(monto_centavos)
            params['reason'] = motivo
            refund = stripe.Refund.create(**params)
            return refund
        except stripe.error.StripeError as e:
            raise Exception(f"Error al reembolsar: {e.user_message}")

    @staticmethod
    def registrar_reembolso(pago: Pago, stripe_refund_id: str, monto: float, motivo: str, usuario):
        """Guarda el reembolso en la BD para auditoría."""
        Reembolso.objects.create(
            pago=pago,
            stripe_refund_id=stripe_refund_id,
            monto=monto,
            motivo=motivo,
            gestionado_por=usuario
        )