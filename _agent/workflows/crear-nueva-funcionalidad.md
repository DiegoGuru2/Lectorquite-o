---
description: Crear una nueva funcionalidad en Arrechoteca API
---
# Workflow: `crear-nueva-funcionalidad`

Este flujo de trabajo asegura que las nuevas características cumplan con la arquitectura del proyecto.

## Paso 1: Definición del Modelo (BD)
1. Abre `models.py`.
2. Crea la(s) nueva(s) clase(s) heredando de `Base`.
3. Define columnas SQL con `Column`, `Integer`, `String`, `ForeignKey`, etc.
4. Establece relaciones bidireccionales con `relationship`.

## Paso 2: Generar Migración
1. En la terminal, ejecuta:
   ```bash
   alembic revision --autogenerate -m "Crear tabla de [nombre_funcionalidad]"
   ```
2. Revisa la migración en `alembic/versions/`.
3. Aplica los cambios a la BD:
   ```bash
   alembic upgrade head
   ```

## Paso 3: Esquemas de Datos (I/O)
1. Busca un archivo existente en `schemas/` para inspirarte o crea uno nuevo: `schemas/[funcionalidad].py`.
2. Define el esquema base heredando de `pydantic.BaseModel`.
3. Separa el esquema de creación (`Create`) y el de consulta (`Response`).
4. Habilita `from_attributes = True` en la clase interna `Config`.

## Paso 4: Router y Controladores (API)
1. Crea el archivo `routers/[funcionalidad].py`.
2. Instancia `APIRouter` con su prefijo y etiquetas descriptivas.
3. Define los endpoints (`@router.get`, `@router.post`, etc.).
4. Usa dependencias para DB y Auth:
   ```python
   db: Session = Depends(get_db)
   user: TokenPayload = Depends(ensure_user_in_db)
   ```

## Paso 5: Registro en `main.py`
1. Abre `main.py`.
2. Importa el nuevo router de `routers`.
3. Regístralo con `app.include_router([nombre].router)`.

## Paso 6: Verificación
1. Inicia la aplicación: `uvicorn main:app --reload`.
2. Verifica el nuevo endpoint en `http://localhost:8000/docs`.
