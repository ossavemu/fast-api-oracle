from fastapi import Request
import oracledb
from ..database.connection import get_db

async def add_admin_status(request: Request, call_next):
    try:
        # Si hay un usuario autenticado, verificar si es admin
        if hasattr(request.state, 'user'):
            db = next(get_db())
            cursor = db.cursor()
            try:
                cursor.execute("""
                    SELECT id_perfil 
                    FROM recycling_app.usuario 
                    WHERE correo = :1
                """, [request.state.user])
                result = cursor.fetchone()
                request.state.is_admin = result[0] == 2 if result else False
            finally:
                cursor.close()
        
        response = await call_next(request)
        return response
    except Exception as e:
        print(f"Error en middleware admin: {str(e)}")
        response = await call_next(request)
        return response 