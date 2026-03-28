from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print(f"Versión de Postgres en 5432: {result.fetchone()[0]}")
