# {{project_name}} - All Context

Last updated: 2026-09-01

This file is the root context entrypoint for the repo.

Use it for two things:
1. quick routing to the right context pack or root file
2. broad architecture and repository understanding

Start here before loading deeper context files.

---

## How This File Works (the `all-*.md` Convention)

Every `process/context/` directory has one `all-*.md` entrypoint that acts as an attachable quick router for that domain. This root file (`all-context.md`) is the top-level router. Context groups each have their own `all-{group}.md` entrypoint.

**The pattern:**

```
process/context/
  all-context.md                      <-- THIS FILE: root router
  planning/
    all-planning.md                   <-- group router for planning
    example-simple-prd.md             <-- deep doc within the group
    example-complex-prd.md            <-- deep doc within the group
  tests/
    all-tests.md                      <-- group router for tests
    debugging-and-pitfalls.md         <-- deep doc within the group
    e2e-tests.md                      <-- deep doc within the group
  database/
    all-database.md                   <-- group router for database
    schema-guide.md                   <-- deep doc within the group
    migration-procedures.md           <-- deep doc within the group
```

**How agents use it:**

1. Agent reads `all-context.md` first (this file)
2. Finds the relevant context group from the routing tables below
3. Reads that group's `all-{group}.md` entrypoint
4. Only then loads the specific deep doc needed

This layered routing keeps context windows small. Never load the whole `process/context/` tree.

**What each `all-{group}.md` must contain:**

- Scope (what the group covers and does NOT cover)
- Read-when rules (when an agent should load this group)
- Quick procedures or decision rules
- Source paths (list of deeper docs in the group)
- Update triggers (when to refresh this group's content)
- Routing to deeper docs within the group

---

## Quick Start

For most substantial tasks:

1. read this file first
2. choose the smallest relevant root file or context group from the tables below
3. only then load deeper files

---

## Current Root Entry Points

<!-- GENERATED:routing -->
| File | Read when |
|---|---|
| `process/context/all-context.md` | any substantial planning, research, review, or implementation task |

## Current Context Groups

| Group | Entry point | Scope |
|---|---|---|
| (no groups yet — populate during STUDY phase as content reaches 3+ durable docs) | | |

## Task Routing Table

<!-- STUDY: Replace this table with routing entries based on actual context groups created. -->
<!-- The "Load first" column always starts with all-context.md. -->
<!-- The "Then load" column points to the group entrypoint, then optionally a deep doc. -->

| If the task involves... | Start with |
|---|---|
| architecture or stack questions | this file |
| testing or verification | `process/context/tests/all-tests.md` |
| creating a new plan | `process/context/planning/all-planning.md` |

---

## Context Group Lifecycle

Context groups are durable knowledge domains, not feature folders.

Create a group when:

- a topic has 3+ durable docs
- a single doc exceeds roughly 800 lines with separable subtopics
- multiple agents repeatedly need only one slice of a large context file
- the topic maps to a stable operational domain (tests, infra, database, auth, UI, workflows, etc.)

Do not create a group when:

- the content is a temporary report
- the content is a plan or execution artifact
- the topic is feature-specific and belongs in `process/features/...`

Move or split one group at a time. Use `all-{group}.md` entrypoints. Run the `audit-context` skill after every context organization change.

---

## Naming Convention

There are no `README.md` files inside `process/context/`.

Canonical entrypoints use `all-*.md`:

- root: `process/context/all-context.md`
- group: `process/context/{group}/all-{group}.md`

Each `all-{group}.md` file should act as the attachable quick router for that domain:

- tell the agent what the group covers
- give quick procedures and decision rules
- route to smaller deeper files

---

## Context Update Protocol

When durable project knowledge changes:

1. update the smallest relevant context file
2. update this file if routing, ownership, naming, or groups changed
3. update the owning `all-{group}.md` entrypoint when a group exists
4. run `audit-context`

---

## Repository Structure

The project is a Django application with the following top-level layout:

```
proyecto_reservas/
  manage.py
  config/                  # Configuración del proyecto (settings, urls)
  core/                    # Aplicación principal: Plazas y Reservas
    __init__.py
    admin.py
    forms.py
    models.py
    urls.py
    views.py
    migrations/
  clientes/                # Aplicación de gestión de usuarios y vehículos
    __init__.py
    admin.py
    apps.py
    decorators.py
    forms.py
    models.py
    migrations/
    static/
    templatetags/
    tests.py
    urls.py
    views.py
  db.sqlite3               # Base de datos residual (PostgreSQL es la entorno real)
  requirements.txt
  templates/               # Plantillas base y componentes
    base.html
    clientes/
    componente/
    core/
    registration/
  venv/                    # Entorno virtual Python
```

---

## Technology Stack

- **Framework:** Django 6.1 (Python)
- **Language:** Python 3.13
- **Database:** PostgreSQL (configurado en `settings.py` en localhost:5433, pero `db.sqlite3` existe como residuo en la raíz)
- **ORM:** Django ORM con psycopg 3.3.4
- **Frontend:** Bootstrap 5.3.3 (vía CDN)
- **Auth:** Django authentication con grupos personalizados (`Establecimientos`)
- **i18n:** Español (`LANGUAGE_CODE = 'es-es'`, `TIME_ZONE = 'Europe/Madrid'`)
- **Package manager:** pip
- **Static files:** `clientes/static/` + Bootstrap CDN

---

## Key Patterns and Conventions

- **Modelos duplicados:** `core` y `clientes` definen ambos `Plaza`, `Reserva`, `Plazo` con estructuras distintas → conflicto potencial en BD si ambos apps están en INSTALLED_APPS
- **Importaciones cruzadas:** `clientes.views` importa `Reserva` desde `clientes.models` (debería ser `core.models`)
- **Forms:** `ReservaForm` filtra automáticamente las plazas libres (`Plaza.objects.filter(ocupada=False)`)
- **Decorators:** `clientes/decorators.py` define `establecimiento_required` para vistas restringidas a establecimientos/admin
- **Admin:** `core.admin` registra `Plaza`+`Reserva`; `clientes.admin` registra todos los modelos (`Reserva`, `Plazo`, `Plaza`, `Cliente`, `Vehiculo`)
- **Urls:** Toda la rutas definidas en `config/urls.py`; `core/urls.py` está vacío (0 líneas)
- **Templates:** Bootstrap 5 via CDN; plantillas anidadadas por app (`core/`, `clientes/`) y compartidas (`base.html`, `componentes/`)
- **Idioma:** Código y plantillas en español (por convenio del curso)
- **Tests:** `clientes/tests.py` existe pero está vacío; sin assertions ni fixtures

---

## Environment and Configuration

**Config files:** `config/settings.py`, `requirements.txt`

**Env var groups (names only, never values):**

- Database: `DATABASE_URL` (formato postgresql://jose:1234@localhost:5433/aparcamiento_db)
- Seguridad: `SECRET_KEY` (establecido en `settings.py`)
- Idioma: `LANGUAGE_CODE = 'es-es'`, `TIME_ZONE = 'Europe/Madrid'`
- Depuración: `DEBUG = True`

---

## Scan Metadata

- Generated: 2026-09-01
- HEAD: /home/cefyet/Documentos/curso_de_programacion/proyecto_fin_curso (project root)
- Mode: vc-setup (Flow A - New Project)
- Package manager: pip
- Project type: Django 6.1 / Python reservar plazas de aparcamiento
- Code scan issues detected: model duplication between core/apps, empty core/urls.py, db.sqlite3 residuo

---

## Context Group Lifecycle (continued)

Move or split one group at a time. Use `all-{group}.md` entrypoints. Run the `audit-context` skill after every context organization change.