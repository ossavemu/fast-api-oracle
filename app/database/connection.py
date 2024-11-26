import oracledb
from ..config import settings

def get_db():
    try:
        # Usar modo thin sin cliente Oracle
        connection = oracledb.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dsn=f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_SERVICE}"
        )
        yield connection
    except Exception as e:
        print(f"Error de conexión: {str(e)}")  # Log para debug
        raise
    finally:
        if 'connection' in locals():
            connection.close() 