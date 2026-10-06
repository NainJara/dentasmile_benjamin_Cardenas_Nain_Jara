# DentaSmile API — Back End Django con Arquitectura Hexagonal

Evaluación 2 · Programación Back End · INACAP.
Back End propio (Django + Django REST Framework) para el Front End React **DentaSmile**,
que antes consumía la API compartida del curso. Autenticación por token en toda la API.

## Las dos entidades

| Entidad | Rol | Tabla | Campos |
|---|---|---|---|
| **Tratamiento** | Principal (catálogo) | `dentasmile_tratamiento` | `id`, `nombre` (único), `descripcion`, `precio` |
| **Cita** | Secundaria (transaccional) | `dentasmile_cita` | `id`, `paciente_nombre`, `paciente_telefono`, `tratamiento` (**ForeignKey → Tratamiento**), `fecha`, `hora`, `estado` |

Paso de Mongo (NoSQL) a relacional:

| Antes (API Mongo) | Ahora (Django / SQLite) |
|---|---|
| `paciente: { nombre, telefono }` | columnas `paciente_nombre`, `paciente_telefono` (aplanado) |
| `tratamientoId` (texto suelto) | `ForeignKey` a `TratamientoModel` |
| `tratamientoNombre` (copiado en cada cita) | no se guarda; la API lo devuelve como `tratamiento_nombre` (solo lectura) usando la FK |
| `_id` (texto) | `id` (entero autoincremental) |

La entidad `Cita` no tenía array de items, por eso **no** se usa `JSONField`.

## Estructura (mapeada al hexágono)

```
dentasmile_project/          configuración de Django (settings, urls raíz)
dentasmile/
├── domain/                  ← CORE: sin Django
│   ├── entities.py            Tratamiento y Cita (dataclasses puros)
│   └── repositories.py        Puertos: TratamientoRepository, CitaRepository
├── application/             ← Casos de uso (lógica de negocio), sin Django ni HTTP
│   ├── use_cases.py           Listar/Obtener/Crear/Actualizar/Eliminar × 2 entidades
│   └── exceptions.py          Errores de negocio
├── infrastructure/          ← Adaptador secundario (persistencia)
│   ├── models.py              TratamientoModel y CitaModel (ORM + ForeignKey)
│   ├── repositories.py        Implementaciones con Django ORM
│   └── di.py                  Decide qué repositorio concreto se usa
├── api/                     ← Adaptador primario (HTTP)
│   ├── serializers.py         JSON <-> entidades de dominio
│   ├── views.py               Reciben HTTP, llaman al caso de uso, responden
│   └── urls.py                Rutas /api/tratamientos/ y /api/citas/
├── migrations/
├── admin.py
└── tests.py                 10 tests (auth, CRUD y reglas de negocio)
```

**Regla de dependencia:** `domain/` y `application/` nunca importan Django, DRF ni HTTP.

## Reglas de negocio (viven en `application/use_cases.py`)

- No puede haber dos tratamientos con el mismo nombre (sin distinguir mayúsculas).
- No se puede eliminar un tratamiento que tiene citas asociadas (`409`).
- Toda cita debe apuntar a un tratamiento que exista (`400`).
- No puede haber dos citas activas en la misma fecha y hora (`409`). Una cita `cancelada` libera su horario.
- `estado` solo admite: `pendiente` (por defecto), `confirmada`, `cancelada`.

## Cómo correrlo (Windows, PowerShell)

```powershell
python -m venv entorno
entorno\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser        # usuario para pedir el token
python manage.py runserver
python manage.py test                   # opcional: corre los tests
```

La API queda en `http://127.0.0.1:8000/api/`. El panel de administración, en `http://127.0.0.1:8000/admin/`.

## Autenticación

1. Pedir el token:

```
POST /api/token/
Content-Type: application/json

{ "username": "<usuario>", "password": "<clave>" }
```

Respuesta: `{ "token": "e534d15b..." }`

2. Enviarlo en **todas** las peticiones (la palabra es `Token`, no `Bearer`):

```
Authorization: Token e534d15b...
```

Sin token, cualquier endpoint responde `401 Unauthorized`.

## Endpoints

| Método | URL | Qué hace | Respuestas |
|---|---|---|---|
| POST | `/api/token/` | Login: devuelve el token | 200 · 400 |
| GET | `/api/tratamientos/` | Lista todos los tratamientos | 200 |
| POST | `/api/tratamientos/` | Crea un tratamiento | 201 · 400 |
| GET | `/api/tratamientos/<id>/` | Detalle de un tratamiento | 200 · 404 |
| PUT | `/api/tratamientos/<id>/` | Actualiza un tratamiento | 200 · 400 · 404 |
| DELETE | `/api/tratamientos/<id>/` | Elimina un tratamiento | 204 · 404 · 409 |
| GET | `/api/citas/` | Lista todas las citas | 200 |
| POST | `/api/citas/` | Crea una cita | 201 · 400 · 409 |
| GET | `/api/citas/<id>/` | Detalle de una cita | 200 · 404 |
| PUT | `/api/citas/<id>/` | Actualiza una cita | 200 · 400 · 404 · 409 |
| DELETE | `/api/citas/<id>/` | Elimina una cita | 204 · 404 |

`PUT` acepta el objeto completo o solo los campos a cambiar.

### Ejemplos de cuerpo (JSON)

Crear tratamiento — `POST /api/tratamientos/`

```json
{ "nombre": "Limpieza Dental", "descripcion": "Limpieza ultrasónica", "precio": 35000 }
```

Crear cita — `POST /api/citas/`

```json
{
  "paciente_nombre": "Benja",
  "paciente_telefono": "+56912345678",
  "tratamiento_id": 1,
  "fecha": "2026-10-10",
  "hora": "15:30",
  "estado": "confirmada"
}
```

Respuesta (`201`):

```json
{
  "id": 1,
  "paciente_nombre": "Benja",
  "paciente_telefono": "+56912345678",
  "tratamiento_id": 1,
  "tratamiento_nombre": "Limpieza Dental",
  "fecha": "2026-10-10",
  "hora": "15:30",
  "estado": "confirmada"
}
```

Errores: `{ "detail": "Ya hay una cita el 2026-10-10 a las 15:30" }`

## Datos iniciales (alineados con el front React)

La tabla de tratamientos parte vacía. El front tiene fijos 5 tratamientos (`001` a `005`); para que
coincidan, créalos en este orden con `POST /api/tratamientos/` (así obtienen los ids 1 a 5):

| id | nombre | precio |
|---|---|---|
| 1 | Limpieza Dental | 35000 |
| 2 | Blanqueamiento Dental | 120000 |
| 3 | Ortodoncia | 0 |
| 4 | Implantes | 0 |
| 5 | Urgencia Dental | 0 |

Ejemplo de cuerpo: `{ "nombre": "Limpieza Dental", "precio": 35000 }`

## Para conectar el Front React más adelante

CORS ya acepta `http://localhost:5173` (Vite). Lo que tendrá que cambiar el front en `src/services/CitaAPI.js`:

| Front actual (API Mongo) | Back nuevo |
|---|---|
| `URL = https://apiclases.inacode.cl/dental` | `http://127.0.0.1:8000/api/citas/` (con `/` final) |
| Sin autenticación | Header `Authorization: Token ...` en cada `fetch` |
| `c._id` | `c.id` |
| `paciente: { nombre, telefono }` | `paciente_nombre`, `paciente_telefono` |
| `tratamientoId: '001'` + `tratamientoNombre` | `tratamiento_id: 1` (entero); `tratamiento_nombre` viene de vuelta |
| Lista: `data.datos \|\| data` | La lista llega directa como arreglo |
| `DELETE` hace `res.json()` | `DELETE` responde `204` sin cuerpo: no llamar a `res.json()` |

Como el front tiene los tratamientos fijos (`001`…`005`), conviene que el `<select>` los lea de `GET /api/tratamientos/`.

## Configurar otra base de datos

El proyecto usa SQLite. Para cambiar de motor (por ejemplo Oracle/FreeSQL) solo se toca
`dentasmile_project/settings.py` (`DATABASES`); `domain/` y `application/` no cambian.
