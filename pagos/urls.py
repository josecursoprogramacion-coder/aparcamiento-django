from django.urls import path
from . import views, webhooks
from clientes.decorators import cliente_required

urlpatterns = [
    path('checkout/<int:reserva_id>/', views.calcular_precio_y_pagar, name='calcular_precio_y_pagar'),
    path('iniciar/<int:pago_id>/', views.iniciar_pago, name='iniciar_pago'),
    path('resultado/<int:pago_id>/', views.pago_resultado, name='pago_resultado'),
    path('reembolsar/<int:pago_id>/', views.reembolsar_pago, name='reembolsar_pago'),
    path('webhook/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
]