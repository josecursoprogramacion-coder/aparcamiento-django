from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
import json
from datetime import datetime
from .models import MensajeEnviado, CodigoTaquilla, Resena
from pagos.models import Pago


# ============================================
# URLs FIJAS DE LAS UBICACIONES
# ============================================
TAQUILLA_DIRECCION = "Calle La Hoz, León"
PARKING_DIRECCION = "Calle Cardenal Landazuri 21, León"

TAQUILLA_COORDS = "42.5982,-5.5686"
PARKING_COORDS = "42.5988,-5.5701"


def generar_enlace_maps_destino(destino_coords, destino_nombre):
    return (
        f"https://www.google.com/maps/dir/?api=1"
        f"&destination={destino_coords}"
        f"&travelmode=driving"
    )


def generar_enlace_maps_entre_puntos(origen_coords, destino_coords):
    return (
        f"https://www.google.com/maps/dir/"
        f"{origen_coords}/{destino_coords}"
        f"?travelmode=walking"
    )


@login_required
def chat_view(request):
    historial = MensajeEnviado.objects.filter(
        user=request.user
    ).order_by('fecha_envio')
    
    tiene_reserva_pagada = Pago.objects.filter(
        usuario=request.user,
        estado='completado'
    ).exists()
    
    return render(request, 'comunicaciones/chat.html', {
        'historial': historial,
        'tiene_reserva_pagada': tiene_reserva_pagada,
    })


@csrf_exempt
def procesar_mensaje(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mensaje_usuario = data.get('mensaje', '').strip().lower()
        seccion = data.get('seccion', 'parking')
        user = request.user
        
        tiene_reserva_pagada = Pago.objects.filter(
            usuario=user,
            estado='completado'
        ).exists()
        
        if seccion == 'parking' and not tiene_reserva_pagada:
            return JsonResponse({
                'respuesta': '🔒 No tienes reserva confirmada. Primero debes realizar una reserva.',
                'botones': [],
                'abrir_url': None
            })
        
        if seccion == 'parking':
            respuesta = generar_respuesta_parking(mensaje_usuario, user)
        else:
            respuesta = generar_respuesta_comunicaciones(mensaje_usuario, user)
        
        MensajeEnviado.objects.create(
            user=user,
            tipo=respuesta['tipo'],
            contenido=respuesta['texto']
        )
        
        return JsonResponse({
            'respuesta': respuesta['texto'],
            'botones': respuesta.get('botones', []),
            'abrir_url': respuesta.get('abrir_url', None)
        })
    
    return JsonResponse({'error': 'Método no permitido'}, status=400)


def generar_respuesta_parking(mensaje, user):
    if any(x in mensaje for x in ['empezar', 'comenzar', 'instrucciones', 'llegar', 'donde', 'direccion', 'ubicacion', 'hola', 'buenas', 'saludos', 'help', 'ayuda', 'inicio']):
        enlace_taquilla = generar_enlace_maps_destino(TAQUILLA_COORDS, "Taquilla Calle La Hoz")
        
        return {
            'tipo': 'instrucciones_taquilla',
            'texto': (
                f"📍 PASO 1 – Cómo llegar a la taquilla:\n\n"
                f"🗺️ Pulsa este enlace y Google Maps te llevará desde tu ubicación actual "
                f"hasta la taquilla:\n\n"
                f"👉 {enlace_taquilla}\n\n"
                f"📌 La taquilla está en: {TAQUILLA_DIRECCION}\n\n"
                f"Cuando llegues, escribe \"codigo\" o pulsa el botón para recibir tu código de apertura."
            ),
            'botones': [
                {'texto': '🔑 Ya estoy aquí, dame el código', 'comando': 'codigo'},
                {'texto': '🔄 Reiniciar', 'comando': 'empezar'}
            ]
        }

    if any(x in mensaje for x in ['codigo', 'apertura', 'abrir', 'clave', 'pin']):
        codigo_obj = CodigoTaquilla.generar_codigo()
        codigo_obj.usado_por = user
        codigo_obj.fecha_uso = datetime.now()
        codigo_obj.activo = False
        codigo_obj.save()
        
        try:
            email = EmailMessage(
                subject='🔑 Tu código de apertura – Taquilla Calle La Hoz',
                body=(
                    f"Hola {user.first_name or user.username},\n\n"
                    f"Tu código de apertura para la taquilla es:\n\n"
                    f"    👉 {codigo_obj.codigo} 👈\n\n"
                    f"Introdúcelo en el teclado de la taquilla para recoger tu mando.\n\n"
                    f"Ubicación: {TAQUILLA_DIRECCION}\n\n"
                    f"¡Gracias!\nEl equipo"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.send()
        except Exception:
            pass
        
        return {
            'tipo': 'codigo_apertura',
            'texto': (
                f"🔑 PASO 2 – Tu código de apertura:\n\n"
                f"Introduce este código en el teclado de la taquilla:\n\n"
                f"    ╔══════════╗\n"
                f"    ║  {codigo_obj.codigo}  ║\n"
                f"    ╚══════════╝\n\n"
                f"📬 También te he enviado el código por email a {user.email}\n\n"
                f"Cuando abras la taquilla y recojas el mando, pulsa el botón de abajo."
            ),
            'botones': [
                {'texto': '🅿️ Ya tengo el mando, llévame al parking', 'comando': 'parking'},
                {'texto': '🔁 Repetir código', 'comando': 'codigo'}
            ]
        }

    if any(x in mensaje for x in ['parking', 'coche', 'recorrido', 'andar', 'caminar', 'llegar al parking']):
        enlace_parking = generar_enlace_maps_entre_puntos(TAQUILLA_COORDS, PARKING_COORDS)
        
        return {
            'tipo': 'enlace_parking',
            'texto': (
                f"🅿️ PASO 3 – Recorrido a pie hasta el parking:\n\n"
                f"🚶 Pulsa este enlace para ver el recorrido a pie:\n\n"
                f"👉 {enlace_parking}\n\n"
                f"📍 Origen: {TAQUILLA_DIRECCION}\n"
                f"📍 Destino: {PARKING_DIRECCION}\n\n"
                f"El trayecto es de aproximadamente 3 minutos andando.\n\n"
                f"🎉 ¡Listo! Ya tienes todo lo que necesitas:\n"
                f"   ✅ Enlace para llegar a la taquilla\n"
                f"   ✅ Código de apertura: {codigo_usado(user)}\n"
                f"   ✅ Recorrido a pie hasta el parking\n\n"
                f"¡Disfruta de tu estancia! 🏰"
            ),
            'botones': [
                {'texto': '🔄 Reiniciar', 'comando': 'empezar'}
            ]
        }

    return {
        'tipo': 'instrucciones_taquilla',
        'texto': (
            "🤔 No entiendo tu mensaje.\n\n"
            "Puedo ayudarte con:\n"
            "1️⃣ 🗺️ Enlace para llegar a la taquilla\n"
            "2️⃣ 🔑 Código de apertura (4 dígitos)\n"
            "3️⃣ 🚶 Recorrido a pie hasta el parking\n\n"
            "Escribe \"empezar\" para volver a empezar."
        ),
        'botones': [
            {'texto': '🔄 Reiniciar', 'comando': 'empezar'}
        ]
    }


def generar_respuesta_comunicaciones(mensaje, user):
    if any(x in mensaje for x in ['hola', 'buenas', 'saludos', 'ayuda', 'inicio', 'empezar', 'comenzar']):
        return {
            'tipo': 'instrucciones_taquilla',
            'texto': (
                "👋 ¡Hola! ¿En qué podemos ayudarte?\n\n"
                "• 📧 Contacto con soporte\n"
                "• ⭐ Dejar una reseña o valoración\n"
                "• 👀 Ver opiniones de otros clientes\n"
                "• ℹ️ Información sobre el servicio"
            ),
            'botones': [
                {'texto': '📧 Contacto', 'comando': 'contacto'},
                {'texto': '⭐ Dejar reseña', 'comando': 'resena'},
                {'texto': '👀 Ver opiniones', 'comando': 'opiniones'}
            ]
        }

    if any(x in mensaje for x in ['resena', 'valorar', 'opinar', 'estrella', 'rating']):
        return {
            'tipo': 'instrucciones_taquilla',
            'texto': (
                "⭐ ¡Nos encantaría tu opinión!\n\n"
                "¿Cómo valoras el servicio? Escribe un número del 1 al 5:\n\n"
                "1 ⭐  →  Muy mal\n"
                "2 ⭐⭐  →  Mal\n"
                "3 ⭐⭐⭐  →  Normal\n"
                "4 ⭐⭐⭐⭐ →  Bien\n"
                "5 ⭐⭐⭐⭐⭐ →  Excelente"
            ),
            'botones': [
                {'texto': '⭐ 1', 'comando': '1'},
                {'texto': '⭐⭐ 2', 'comando': '2'},
                {'texto': '⭐⭐⭐ 3', 'comando': '3'},
                {'texto': '⭐⭐⭐⭐ 4', 'comando': '4'},
                {'texto': '⭐⭐⭐⭐⭐ 5', 'comando': '5'},
            ]
        }

    if mensaje.isdigit() and 1 <= int(mensaje) <= 5:
        Resena.objects.create(
            user=user,
            rating=int(mensaje),
            comentario=''
        )
        estrellas = '⭐' * int(mensaje)
        return {
            'tipo': 'instrucciones_taquilla',
            'texto': (
                f"✅ ¡Gracias por tu valoración! {estrellas}\n\n"
                f"Tu opinión nos ayuda a mejorar. "
                f"¿Quieres añadir algún comentario? Escríbelo ahora, "
                f"o escribe \"gracias\" para terminar."
            ),
            'botones': [
                {'texto': '✅ Gracias, ya terminé', 'comando': 'gracias'},
                {'texto': '🔄 Volver al inicio', 'comando': 'empezar'}
            ]
        }

    if any(x in mensaje for x in ['gracias', 'fin', 'terminar', 'listo', 'adios']):
        return {
            'tipo': 'instrucciones_taquilla',
            'texto': (
                "🙏 ¡Gracias a ti! Ha sido un placer ayudarte.\n\n"
                "Si necesitas ayuda en el futuro, solo escribe \"hola\"."
            ),
            'botones': [
                {'texto': '🔄 Volver al inicio', 'comando': 'empezar'},
                {'texto': '📧 Contacto', 'comando': 'contacto'}
            ]
        }

    if any(x in mensaje for x in ['contacto', 'incidencia', 'problema', 'queja']):
        return {
            'tipo': 'instrucciones_taquilla',
            'texto': (
                "📧 Puedes contactarnos de varias formas:\n\n"
                "1. 📋 Formulario en nuestra web\n"
                "2. 📱 Por este mismo chat, escríbeme el problema\n"
                "3. 📞 Teléfono: 987 654 321\n\n"
                "Si es una incidencia con la taquilla, indícame:\n"
                "   • Qué ha pasado\n"
                "   • Tu código de apertura (si lo tienes)\n\n"
                "Un agente te responderá lo antes posible. 💬"
            ),
            'botones': [
                {'texto': '📋 Ir al formulario', 'comando': 'ir_a_formulario'},
                {'texto': '🔄 Volver al inicio', 'comando': 'empezar'}
            ]
        }

    if 'ir_a_formulario' in mensaje or 'formulario' in mensaje:
        return {
            'tipo': 'instrucciones_taquilla',
            'texto': "📋 Abriendo formulario de contacto...",
            'botones': [
                {'texto': '🔄 Volver al chat', 'comando': 'empezar'}
            ],
            'abrir_url': '/comunicaciones/contacto/'
        }

    if any(x in mensaje for x in ['opiniones', 'opiniones', 'reseñas', 'valoraciones', 'opinar']):
        resenas = Resena.objects.order_by('-fecha_creacion')[:5]
        if resenas:
            texto = "⭐ Últimas opiniones de nuestros clientes:\n\n"
            for r in resenas:
                estrellas = '⭐' * r.rating
                texto += f"{estrellas} - {r.user.username}\n"
            texto += "\n¿Quieres dejar tu opinión?"
        else:
            texto = "Aún no hay opiniones. Sé el primero en valorar nuestro servicio."
        
        return {
            'tipo': 'instrucciones_taquilla',
            'texto': texto,
            'botones': [
                {'texto': '⭐ Dejar mi reseña', 'comando': 'resena'},
                {'texto': '🔄 Volver al inicio', 'comando': 'empezar'}
            ]
        }

    return {
        'tipo': 'instrucciones_taquilla',
        'texto': (
            "🤔 No entiendo tu mensaje.\n\n"
            "Puedo ayudarte con:\n"
            "• 📧 Contacto con soporte\n"
            "• ⭐ Dejar una reseña\n"
            "• 👀 Ver opiniones\n\n"
            "Escribe \"hola\" para ver las opciones."
        ),
        'botones': [
            {'texto': '📧 Contacto', 'comando': 'contacto'},
            {'texto': '⭐ Dejar reseña', 'comando': 'resena'},
            {'texto': '👀 Ver opiniones', 'comando': 'opiniones'}
        ]
    }


def codigo_usado(user):
    ultimo = CodigoTaquilla.objects.filter(usado_por=user).order_by('-fecha_uso').first()
    return ultimo.codigo if ultimo else "No se ha generado aún"


@login_required
def contacto_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto')
        mensaje_texto = request.POST.get('mensaje')
        
        MensajeEnviado.objects.create(
            user=request.user,
            tipo='instrucciones_taquilla',
            contenido=f'{nombre} ({email}): {mensaje_texto}'
        )
        
        try:
            email_msg = EmailMessage(
                subject=f'Consulta: {asunto}',
                body=f'Nombre: {nombre}\nEmail: {email}\n\nMensaje:\n{mensaje_texto}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['admin@tuempresa.com'],
            )
            email_msg.send()
        except Exception:
            pass
        
        messages.success(request, '✅ ¡Mensaje enviado! Te responderemos pronto.')
        return redirect('contacto')
    
    return render(request, 'comunicaciones/contacto.html')


@login_required
def resenas_view(request):
    mis_resenas = Resena.objects.filter(user=request.user).order_by('-fecha_creacion')
    return render(request, 'comunicaciones/resenas.html', {'resenas': mis_resenas})


def conocenos_view(request):
    resenas = Resena.objects.order_by('-fecha_creacion')[:10]
    return render(request, 'comunicaciones/conocenos.html', {'resenas': resenas})