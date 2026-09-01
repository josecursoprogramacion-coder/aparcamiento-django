# Proyecto de Reservas de Aparcamiento

## 📋 Descripción
Desarrollo de una aplicación web completa para la gestión y reserva de plazas de aparcamiento. El sistema permite gestionar 30 plazas, controlar la disponibilidad por días y administrar los datos de clientes, vehículos y reservas.

El proyecto está desarrollado con **Python** y **Django**, utilizando **PostgreSQL** como base de datos y **Bootstrap 5** para la interfaz de usuario.

## 🎯 Objetivos del Proyecto
- Implementar un sistema de reservas de días completos para 30 plazas.
- Gestionar diferentes perfiles de usuario con permisos diferenciados.
- Controlar la disponibilidad de plazas y la asignación de vehículos.
- Proporcionar un panel de administración robusto para la gestión interna.

## 👥 Usuarios y Perfiles
La aplicación distingue cuatro tipos de usuarios, gestionados mediante el sistema de autenticación y grupos de Django:

1.  **Visitante (Sin registrar):**
    - Puede ver el listado de plazas disponibles.
    - No puede realizar reservas.
2.  **Cliente (Registrado):**
    - Puede gestionar sus propios vehículos.
    - Puede realizar reservas para sus vehículos en plazas libres.
    - Puede ver su historial de reservas.
3.  **Establecimiento:**
    - Puede gestionar las plazas (editar tipo, precio).
    - Puede ver el estado general del aparcamiento.
    - Puede gestionar reservas (confirmar/cancelar).
4.  **Administrador:**
    - Acceso total al panel de administración de Django.
    - Gestión de usuarios y grupos.
    - Acceso a estadísticas y reportes.

## 🏗️ Estructura del Proyecto
Siguiendo la arquitectura modular aprendida, el proyecto se divide en:

```text
aparcamiento_project/
├── config/                  # Configuración del proyecto (settings, urls)
├── aparcamiento/            # Aplicación principal: Plazas y Reservas
│   ├── models.py            # Modelos: Plaza, Reserva
│   ├── views.py             # Lógica de negocio y vistas
│   ├── forms.py             # Formularios (ModelForm)
│   ├── urls.py
│   └── templates/
├── clientes/                # Aplicación de gestión de usuarios y vehículos
│   ├── models.py            # Modelos: Cliente, Vehiculo
│   ├── views.py             # Gestión de perfil y vehículos
│   ├── forms.py
│   ├── decorators.py        # Decoradores personalizados (ej: cliente_required)
│   └── templates/
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
├── templates/               # Plantillas base y componentes (navbar, footer)
├── manage.py
└── requirements.txt