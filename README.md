# 🚗 Sistema de Gestión y Reservas de Aparcamiento

Aplicación web profesional desarrollada en **Python y Django** para la gestión integral y reserva de plazas de aparcamiento. El sistema permite administrar la disponibilidad de espacios, control de vehículos de clientes, reservas con pago integrado y control de permisos por roles.

---

## 📋 Características Principales

- **Mapa Interactivo:** Mapa visual con planos reales de cada planta (Sótano 1, Sótano 2, Planta 0) y marcadores SVG que muestran el estado en tiempo real de cada plaza.
- **Gestión de Plazas:** Administración de plazas de aparcamiento con coordenadas en mapa, control por nivel y estadísticas de uso con gráficos.
- **Reservas Multi-día:** Selección de rango de fechas con cálculo automático del precio total (15€/día).
- **Pasarela de Pago Stripe:** Integración completa con Stripe para pagos con Tarjeta, Bizum, Apple Pay y Google Pay. Webhooks para confirmación automática.
- **Reembolsos:** Reembolsos totales y parciales directamente desde el panel de administración.
- **Control de Clientes y Vehículos:** Registro de usuarios con perfiles asociados y gestión de vehículos vinculados por matrícula.
- **Roles y Permisos:**
  - **Visitante:** Visualización de plazas libres.
  - **Cliente:** Reservas, pagos, gestión de perfil y vehículos.
  - **Establecimiento/Admin:** Gestión completa de plazas, reservas, reembolsos y estadísticas.

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.13 / Django 6.1
- **Base de Datos:** PostgreSQL (puerto 5433)
- **Frontend:** Bootstrap 5.3.3, HTML5, CSS3, Chart.js (estadísticas)
- **Pagos:** Stripe (Tarjeta, Bizum, Apple Pay, Google Pay)
- **Plantillas:** Django templates modularizadas con componentes reutilizables

---

## 🏗️ Estructura del Proyecto

```text
proyecto_fin_curso/
├── config/                  # Configuración central (settings.py, urls.py, context_processors.py)
├── core/                    # Modelo de negocio (Plaza, Plazo, Reserva) y vistas principales
├── clientes/                # Usuarios, perfiles Cliente, Vehículos y decoradores de acceso
├── pagos/                   # Integración Stripe (Pago, Reembolso, Webhooks, Services)
├── templates/               # Plantillas globales y por app
│   ├── base.html            # Plantilla base con bloque scripts
│   ├── componentes/         # Navbar, footer reutilizables
│   ├── core/                # Mapa, reservas, gestión de plazas y reservas
│   ├── pagos/               # Checkout y resultado de pago
│   └── registration/        # Login, registro
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
│   └── img/planos/          # Planos JPG de cada planta (1754x1240px)
├── process/                 # Documentación de procesos y planes (Harness RIPER-5)
├── manage.py
└── requirements.txt
```

---

## 🗄️ Modelo de Datos

### App `core`
| Modelo | Campos clave | Descripción |
|--------|-------------|-------------|
| **Plaza** | numero, nivel, pixel_x, pixel_y, radio, activo | Plaza de aparcamiento con posición en mapa |
| **Plazo** | plaza (FK), fecha_inicio, fecha_fin, precio, disponible | Franja temporal disponible para una plaza |
| **Reserva** | cliente (FK), vehiculo (FK), plazo (FK), fecha_fin, estado, fecha_creacion | Reserva con rango de fechas |

### App `clientes`
| Modelo | Campos clave | Descripción |
|--------|-------------|-------------|
| **Cliente** | usuario (OneToOne), direccion, telefono, nif | Perfil de cliente |
| **Vehiculo** | cliente (FK), marca, modelo, matricula, color | Vehículo registrado |

### App `pagos`
| Modelo | Campos clave | Descripción |
|--------|-------------|-------------|
| **Pago** | reserva (OneToOne), usuario, stripe_payment_intent_id, monto, estado, metodo_pago | Pago integrado con Stripe |
| **Reembolso** | pago (FK), stripe_refund_id, monto, motivo, estado, gestionado_por | Registro de reembolsos |

---

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/josecursoprogramacion-coder/aparcamiento-django.git
cd aparcamiento-django
```

### 2. Configurar entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto:
```env
# Base de datos
DB_NAME=aparcamiento_db
DB_USER=jose
DB_PASSWORD=1234
DB_HOST=localhost
DB_PORT=5433

# Stripe (obtener claves en dashboard.stripe.com)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 5. Aplicar migraciones y crear superusuario
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Ejecutar el servidor
```bash
python manage.py runserver
```
Accede en `http://127.0.0.1:8000/`

### 7. Configurar webhook de Stripe (para pagos)
```bash
# Instalar Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:8000/pagos/webhook/stripe/
```
Copia el `whsec_...` que te da la CLI en tu `.env`.

---

## 💳 Pasarela de Pago (Stripe)

### Métodos soportados
- **Tarjeta** de crédito/débito
- **Bizum** (España)
- **Apple Pay / Google Pay**

### Flujo de pago
```
Seleccionar plaza → Crear reserva (pendiente) → Checkout Stripe
    → Seleccionar método de pago → Introducir datos
    → Pago confirmado → Reserva confirmada
```

### Tarjetas de prueba
| Tarjeta | Resultado |
|---------|-----------|
| `4242 4242 4242 4242` | ✅ Pago exitoso |
| `4000 0000 0000 0341` | ❌ Pago rechazado |
| `4000 0000 0000 3220` | ⚠️ Requiere 3DS |

### Configurar Bizum en Stripe Dashboard
1. Ve a **Settings → Payment methods**
2. Activa **Bizum**
3. Recarga el checkout

---

## 📊 Panel de Administración

### Gestionar Plazas (`/admin/gestionar-plazas/`)
- Tabla de plazas con estado (Libre/Ocupada)
- **Gráfico de barras:** Reservas históricas por plaza
- **Gráfico circular:** Distribución por nivel
- **Gráfico de línea:** Ocupación diaria (últimos 30 días)

### Gestionar Reservas (`/admin/reservas/gestionar/`)
- Lista completa de reservas con datos de cliente y pago
- **Cancelar** reservas activas
- **Reembolsar** pagos (total o parcial) con selección de motivo

### Gestionar Pagos (`/admin/pagos/`)
- Lista de pagos con estado y método
- **Reembolsar** pagos (total o parcial) con generación de `stripe.refund.id`
- Filtros por fecha, método de pago y estado

## 🤖 Sistema de Agentes y Metodología RIPER-5

Este proyecto utiliza el **sistema de agentes vibecode** para el desarrollo guiado por especificaciones. La estructura se encuentra en los directorios `process/` y `.claude/`:

- **`process/context/`**: Contexto duradero del repositorio (`all-context.md`, `all-tests.md`, y grupos de contexto).
- **`process/general-plans/`** y **`process/features/`**: Almacenamiento de planes, reportes y referencias por features.
- **`.claude/agents/`** y **`.claude/skills/`**: Agentes y skills especializados (research, innovate, plan, execute, debugger, tester, code-simplifier, etc.).
- **Metodología RIPER-5**: Flujo faseado (RESEARCH → INNOVATE → PLAN → EXECUTE → UPDATE PROCESS) para asegurar calidad y documentación en cada etapa.
- **Herramientas clave**: `vc-setup` (scaffolding), `vc-generate-plan` (planes implementables), `vc-audit-vc` (auditoría de salud del harness), `vc-update` / `vc-publish` (actualización y publicación del kit).

## 📁 Estructura de Carpetas del Harness

```text
process/
  _seeds/                 -- Plantillas seed (referencia, nunca modificadas)
  context/                -- Contexto duradero (all-context.md es el router raíz)
  development-protocols/  -- Metodología RIPER-5 y protocolos del proyecto
  general-plans/          -- Planes transversales (active/completed/backlog)
  features/               -- Almacenamiento feature-scoped (core-plazas-y-reservas, clientes-y-vehiculos)
```

---

## 🧪 Pruebas
```bash
python manage.py test
```

---

## 📁 URLs Principales

| URL | Descripción | Requiere |
|-----|-------------|----------|
| `/` | Página de inicio | - |
| `/mapa/` | Mapa interactivo de plazas | - |
| `/mis-reservas/` | Reservas del usuario | Cliente |
| `/pagos/checkout/<id>/` | Checkout de pago Stripe | Cliente |
| `/admin/gestionar-plazas/` | Gestión y estadísticas de plazas | Admin |
| `/admin/reservas/gestionar/` | Gestión de reservas y reembolsos | Admin |
