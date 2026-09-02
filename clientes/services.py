# clientes/services.py

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

try:
    from twilio.rest import Client
except ImportError:
    Client = None


class NotificationService:
    """
    Servicio centralizado para enviar correos y SMS.
    """

    @staticmethod
    def enviar_correo_asunto_recibiente_cuerpo(recipient_email, asunto, cuerpo_html, usuario):
        """
        Envía un correo electrónico.
        """
        try:
            send_mail(
                subject=asunto,
                message='',
                html_message=cuerpo_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            messages.success(usuario, '✅ Confirmación enviada a tu correo electrónico.')
            return True
        except Exception as e:
            messages.error(usuario, f'⚠️ Error al enviar correo: {str(e)}')
            return False

    @staticmethod
    def enviar_sms_telefono_mensaje(recipient_phone, mensaje, usuario):
        """
        Envía un SMS usando Twilio.
        """
        if not getattr(settings, 'TWILIO_ACCOUNT_SID', None):
            messages.warning(usuario, 'ℹ️ Servicio de SMS no configurado en este entorno.')
            return False

        if not Client:
            messages.warning(usuario, 'ℹ️ Librería Twilio no instalada.')
            return False

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            client.messages.create(
                body=mensaje,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=recipient_phone
            )
            
            messages.success(usuario, '✅ Confirmación enviada a tu SMS.')
            return True
        except Exception as e:
            messages.error(usuario, f'⚠️ Error al enviar SMS: {str(e)}')
            return False

    @staticmethod
    def enviar_confirmacion_reserva(usuario, reserva, plazo):
        """
        Envía confirmación de reserva por email y SMS.
        """
        nombre = usuario.username
        email = usuario.email
        telefono = None
        if hasattr(usuario, 'cliente_perfil') and usuario.cliente_perfil.telefono:
            telefono = usuario.cliente_perfil.telefono

        asunto = f"Reserva Confirmada - Plaza {plazo.plaza.numero}"
        cuerpo_correo = f"""
        <h2>¡Tu reserva ha sido confirmada!</h2>
        <p>Hola <strong>{nombre}</strong>,</p>
        <p>Tu plaza de aparcamiento ha sido reservada correctamente.</p>
        <ul>
            <li><strong>Plaza:</strong> {plazo.plaza.numero}</li>
            <li><strong>Fecha:</strong> {plazo.fecha}</li>
            <li><strong>Horario:</strong> {plazo.horario_desde} - {plazo.horario_hasta}</li>
            <li><strong>Total:</strong> €{plazo.precio}</li>
        </ul>
        <p>¡Gracias por usar nuestro servicio!</p>
        """

        mensaje_sms = f"Reserva confirmada. Plaza {plazo.plaza.numero} el {plazo.fecha}. Hora {plazo.horario_desde}. Total: {plazo.precio}€."

        if email:
            NotificationService.enviar_correo_asunto_recibiente_cuerpo(email, asunto, cuerpo_correo, usuario)

        if telefono:
            if not telefono.startswith('+'):
                telefono = '+' + telefono
            NotificationService.enviar_sms_telefono_mensaje(telefono, mensaje_sms, usuario)
