from django.urls import path
from . import views


urlpatterns = [
    path('chat/', views.chat_view, name='chat_view'),
    path('procesar_mensaje/', views.procesar_mensaje, name='procesar_mensaje'),
    path('contacto/', views.contacto_view, name='contacto'),
    path('resenas/', views.resenas_view, name='resenas'),
    path('conocenos/', views.conocenos_view, name='conocenos'),
]