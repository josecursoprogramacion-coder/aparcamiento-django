# 🚗 Sistema de Gestión y Reservas de Aparcamiento

Aplicación web profesional desarrollada en **Python y Django** para la gestión integral y reserva de plazas de aparcamiento. El sistema permite administrar la disponibilidad de espacios, control de vehículos de clientes, franjas horarias y control de permisos por roles mediante grupos de usuario.

---

## 📋 Características Principales

- **Gestión de Plazas y Plazos:** Administración de plazas de aparcamiento con clasificación por tipo (*Normal, Premium, Eléctrico*), control de franjas horarias (`Plazo`) y panel de gestión de plazas para establecimientos.
- **Control de Clientes y Vehículos:** Registro de usuarios con perfiles asociados y gestión individual de vehículos vinculados por matrícula.
- **Sistema de Reservas:** Creación, consulta de historial y cancelación de reservas con comprobación de disponibilidad en tiempo real.
- **Roles y Permisos Diferenciados:**
  - **Visitante:** Visualización de plazas libres.
  - **Cliente:** Gestión de perfil, vehículos y reservas personales.
  - **Establecimiento:** Control operativo global y cancelación/gestión de reservas con decoradores de seguridad personalizados (`establecimiento_required`).
  - **Administrador:** Acceso completo al panel de administración de Django para supervisión y estadísticas.

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.13 / Django 6.1
- **Base de Datos:** PostgreSQL (con soporte para `psycopg`)
- **Frontend:** Bootstrap 5.3.3 (vía CDN), HTML5, CSS3, plantillas modularizadas de Django
- **Control de Calidad / Harness:** Sistema integrado de agentes y metodologías RIPER-5 para desarrollo guiado por especificaciones.

---

## 🏗️ Estructura del Proyecto

La arquitectura sigue un diseño modular dividido en aplicaciones independientes dentro de Django:

```text
proyecto_fin_curso/
├── config/                  # Configuración central del proyecto (settings.py, urls.py, wsgi/asgi)
├── core/                    # Aplicación principal de negocio (Plazas, Reservas, Plazos, vistas y formularios)
├── clientes/                # Gestión de usuarios, perfiles de Cliente, Vehículos y decoradores de acceso
├── templates/               # Plantillas globales (base.html, componentes de navegación/footer, login/registro)
├── process/                 # Documentación de procesos, contexto del repositorio y planes de desarrollo (Harness)
├── manage.py                # Utilidad de línea de comandos de Django
└── requirements.txt         # Dependencias del proyecto
```

---

## 🚀 Guía de Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/josecursoprogramacion-coder/aparcamiento-django.git
cd aparcamiento-django
```

### 2. Configurar el entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos
Asegúrate de tener un servidor PostgreSQL ejecutándose en el puerto configurado (`localhost:5433` con base de datos `aparcamiento_db`), o ajusta los parámetros en `config/settings.py`.

### 5. Aplicar migraciones y crear superusuario
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```
Accede a la aplicación en tu navegador en `http://127.0.0.1:8000/`.

---

## 🧪 Pruebas y Verificación
Para verificar el estado del sistema y la ejecución de tests unitarios/integrados:
```bash
python manage.py test
```
