# Skill: Arrechoteca API Development (Premium Standard)

Esta skill guía el desarrollo de nuevas funcionalides en la API de Arrechoteca Backend (FastAPI + SQLAlchemy).

> [!IMPORTANT]
> - Esta skill extiende las [Mejores Prácticas Universales de FastAPI](../../fastapi_sqlalchemy_best_practices/SKILL.md).
> - Referencia de Estructura de Datos: [Guía de la Base de Datos](./DATABASE.md).

## 📅 Estándares del Proyecto (Arrechoteca)

### 1. Modelos SQLAlchemy (`models.py`)
- Define las tablas con sus tipos de datos y relaciones.
- Usa siempre `primary_key`, `index` y `nullable` según convenga.
- Documenta relaciones con `relationship`.
- **Regla Arrechoteca**: Todas las tablas nuevas deben incluir `is_active = Column(Boolean, default=False)` si requieren moderación.

### 2. Esquemas Pydantic (`schemas/`)
- Separa la validación de entrada (`Create`, `Update`) y de salida (`Base`, con ID).
- Habilita `from_attributes = True` para lectura desde SQLAlchemy.
- Usa tipos de `typing` (`List`, `Annotated`, etc.) para documentación.

### 3. Controladores y Rutas (`routers/`)
- Añade metatada a cada ruta para el Swagger: `summary`, `description`, `response_model`, `tags`.
- Usa siempre `Depends(get_db)` para inyectar la sesión de la base de datos.
- Sigue el patrón RESTful: `GET` para leer, `POST` para crear, `PUT` para actualizar, `DELETE` para eliminar.

## 🛠️ Procedimiento para Agregar Funcionalidad (Master Workflow)

Para implementar una nueva característica (ej: Modulo de Insultos, Comentarios), sigue el [Workflow: crear-nueva-funcionalidad](../../workflows/crear-nueva-funcionalidad.md).

1. **Definir el Modelo (BD)**.
2. **Generar la Migración de Alembic**.
3. **Esquemas Pydantic (I/O)**.
4. **Router y registro en main.py**.
5. **Seguridad JWT (Supabase)**.

## 🔒 Seguridad y Autenticación
- Los endpoints que modifiquen datos DEBEN estar protegidos.
- Utiliza `Depends(ensure_user_in_db)` para validar usuarios.

---
*Arrechoteca: El diccionario más firme de Guayaquil, programado con los más altos estándares.*
