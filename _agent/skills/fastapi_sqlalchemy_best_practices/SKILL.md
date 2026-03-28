# Skill: FastAPI & SQLAlchemy - Mejores Prácticas Universales (Industry Standards)

Esta skill define el estándar de oro para el desarrollo de backends robustos, escalables y seguros utilizando Python (FastAPI + SQLAlchemy + Pydantic).

---

## 🏗️ 1. Arquitectura y Estructura (Clean Architecture)
- **Desacoplo de Capas**: Mantén los modelos de base de datos (`models`) separados de las validaciones de comunicación (`schemas/DTOs`).
- **Controladores Delgados**: La lógica pesada de negocio debe ir en servicios independientes o manejadores especializados, no directamente en el router.
- **Inyección de Dependencias**: Utiliza siempre `Depends()` para servicios, sesiones de base de datos y autenticación.

## 🐍 2. Estándares de Codificación de Python
- **Tipado Estricto (Type Hinting)**: Usa `typing.Annotated` para mayor legibilidad y soporte de herramientas automáticas.
- **Asincronía**: Usa `async/await` solo cuando sea necesario (I/O intensivo). Para ORMs sincrónicos como SQLAlchemy clásico, usa definiciones `def` normales en los routers para evitar bloquear el event loop.
- **Nomenclatura**:
  - Clases: `PascalCase`.
  - Funciones/Variables: `snake_case`.
  - Constantes: `UPPER_CASE`.

## 💎 3. Validación y Modelos (Pydantic & SQLAlchemy)
- **Modelos de Respuesta**: Cada endpoint DEBE definir un `response_model` para evitar fugar información sensible.
- **Configuración de Pydantic**: Usa `from_attributes = True` (Pydantic v2) para permitir la conversión automática de objetos ORM a schemas.
- **Campos Opcionales**: Usa `| None = None` para mayor compatibilidad con Python 3.10+.

## 🔒 4. Seguridad y Robustez
- **Middlewares Seguros**: Configura siempre CORS de manera restrictiva en producción.
- **Validación de Usuarios**: No confíes solo en el ID; utiliza dependencias que validen el token JWT en cada petición sensible.
- **Variables de Entorno**: Nunca hardcodees secretos. Usa `pydantic-settings` o `python-dotenv`.

## 🚨 5. Manejo de Errores y Transacciones
- **HTTP Exceptions**: Lanza errores con códigos de estado semánticos (400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity).
- **Consistencia de BD**: Asegura siempre el cierre de sesiones y realiza `rollback()` en bloques `try/except` cuando una operación falle.

## 📖 6. Documentación Automática (Standard API)
- **Metadata**: Añade `summary` y `description` a cada ruta.
- **Tags**: Agrupa rutas por dominios (ej: "Usuarios", "Pagos", "Productos").
- **Explicación de Parámetros**: Provee valores `default` y descripciones en `Query()` y `Path()`.

---
*Este estándar permite que cualquier proyecto, sea de jerga guayaca o de comercio electrónico, mantenga la más alta calidad de ingeniería.*
