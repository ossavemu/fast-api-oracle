from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.reciclaje import Reciclaje
from ..database.connection import get_db
from typing import List
import oracledb
from ..utils.security import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

def calcular_puntos(cantidad: int, puntos_botella: int) -> int:
    return cantidad * puntos_botella

def calcular_total(puntos: int, puntos_bono: int) -> int:
    return puntos + puntos_bono

@router.get("/reciclaje/", response_class=HTMLResponse)
async def get_reciclajes_view(
    request: Request, 
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Verificar si es admin
        cursor.execute("""
            SELECT id_perfil 
            FROM recycling_app.usuario 
            WHERE correo = :1
        """, [current_user])
        is_admin = cursor.fetchone()[0] == 2

        cursor.execute("""
            SELECT 
                r.id_reciclaje,
                e.nombre as nombre_evento,
                u.nombre || ' ' || u.apellido as nombre_usuario,
                t.nombre as tipo_reciclaje,
                t.puntos_botella as puntos_por_unidad,
                r.cantidad,
                r.puntos,
                r.puntos_bono,
                r.puntos_totales,
                e.fecha,
                u.correo as correo_usuario
            FROM recycling_app.reciclaje r
            JOIN recycling_app.evento e ON r.id_evento = e.id_evento
            JOIN recycling_app.usuario u ON r.id_usuario = u.id_usuario
            JOIN recycling_app.tipo_reciclaje t ON e.id_tipo_reciclaje = t.id_tipo_reciclaje
            ORDER BY e.fecha DESC, r.id_reciclaje DESC
        """)
        results = cursor.fetchall()
        
        reciclajes = []
        for row in results:
            reciclaje = {
                "id_reciclaje": row[0],
                "nombre_evento": row[1],
                "nombre_usuario": row[2],
                "tipo_reciclaje": row[3],
                "puntos_por_unidad": row[4],
                "cantidad": row[5],
                "puntos": row[6],
                "puntos_bono": row[7],
                "puntos_totales": row[8],
                "fecha": row[9].strftime('%Y-%m-%d'),
                "correo_usuario": row[10]
            }
            reciclajes.append(reciclaje)
        
        return templates.TemplateResponse(
            "reciclaje/list.html",
            {
                "request": request, 
                "reciclajes": reciclajes,
                "current_user": current_user,
                "is_admin": is_admin
            }
        )
    except Exception as e:
        print(f"DEBUG: Error al obtener reciclajes: {str(e)}")  # Log para debug
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/reciclaje/create", response_class=HTMLResponse)
async def create_reciclaje_form(
    request: Request, 
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Obtener eventos disponibles con su tipo de reciclaje
        cursor.execute("""
            SELECT e.id_evento, e.nombre, t.puntos_botella, t.nombre as tipo_reciclaje
            FROM recycling_app.evento e
            JOIN recycling_app.tipo_reciclaje t ON e.id_tipo_reciclaje = t.id_tipo_reciclaje
            ORDER BY e.fecha DESC
        """)
        eventos = cursor.fetchall()

        return templates.TemplateResponse(
            "reciclaje/create.html",
            {
                "request": request, 
                "eventos": eventos
            }
        )
    finally:
        cursor.close()

@router.post("/reciclaje/create")
async def create_reciclaje_submit(
    request: Request,
    current_user: str = Depends(get_current_user),
    id_evento: int = Form(...),
    cantidad: int = Form(...),
    bonos: list = Form([]),  # IDs de los bonos seleccionados
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Obtener id_usuario del correo actual
        cursor.execute(
            "SELECT id_usuario FROM recycling_app.usuario WHERE correo = :1",
            [current_user]
        )
        id_usuario = cursor.fetchone()[0]

        # Obtener puntos por botella del tipo de reciclaje del evento
        cursor.execute("""
            SELECT t.puntos_botella
            FROM recycling_app.evento e
            JOIN recycling_app.tipo_reciclaje t ON e.id_tipo_reciclaje = t.id_tipo_reciclaje
            WHERE e.id_evento = :1
        """, [id_evento])
        puntos_botella = cursor.fetchone()[0]

        # Calcular puntos base
        puntos = cantidad * puntos_botella

        # Calcular puntos de bonos
        puntos_bono = 0
        if bonos:
            # Convertir a lista si es un solo valor
            if isinstance(bonos, str):
                bonos = [bonos]
            
            # Crear lista de parámetros para la consulta
            params = [int(b) for b in bonos]
            params.append(id_evento)  # Agregar id_evento al final
            # Obtener la suma de puntos de los bonos seleccionados
            placeholders = ','.join([':' + str(i+1) for i in range(len(bonos))])
            cursor.execute(f"""
                SELECT SUM(valor_puntos)
                FROM recycling_app.bonos
                WHERE id_bono IN ({placeholders})
                AND id_evento = :evento
            """, [*bonos, id_evento])  # Verificar que los bonos pertenezcan al evento
            puntos_bono = cursor.fetchone()[0] or 0

        puntos_totales = puntos + puntos_bono

        # Insertar reciclaje
        cursor.execute("SELECT recycling_app.reciclaje_seq.NEXTVAL FROM DUAL")
        id_reciclaje = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO recycling_app.reciclaje 
            (id_reciclaje, id_evento, id_usuario, cantidad, puntos, puntos_bono, puntos_totales)
            VALUES (:1, :2, :3, :4, :5, :6, :7)
        """, [id_reciclaje, id_evento, id_usuario, cantidad, puntos, puntos_bono, puntos_totales])

        db.commit()
        return RedirectResponse(url="/reciclaje/", status_code=303)
    except Exception as e:
        db.rollback()
        print(f"Error al crear reciclaje: {str(e)}")
        return templates.TemplateResponse(
            "reciclaje/error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )
    finally:
        cursor.close()

@router.get("/reciclaje/edit/{id_reciclaje}", response_class=HTMLResponse)
async def edit_reciclaje_form(
    request: Request, 
    id_reciclaje: int, 
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Verificar si es admin
        cursor.execute("""
            SELECT id_perfil 
            FROM recycling_app.usuario 
            WHERE correo = :1
        """, [current_user])
        is_admin = cursor.fetchone()[0] == 2

        # Obtener el reciclaje
        cursor.execute("""
            SELECT r.*, u.correo
            FROM recycling_app.reciclaje r
            JOIN recycling_app.usuario u ON r.id_usuario = u.id_usuario
            WHERE r.id_reciclaje = :1
        """, [id_reciclaje])
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Reciclaje no encontrado")
        
        # Permitir edición solo al dueño o admin
        if not is_admin and row[-1] != current_user:
            raise HTTPException(status_code=403, detail="No tienes permiso para editar este reciclaje")
        
        reciclaje = Reciclaje(
            id_reciclaje=row[0],
            id_evento=row[1],
            id_usuario=row[2],
            cantidad=row[3],
            puntos=row[4],
            puntos_bono=row[5],
            puntos_totales=row[6]
        )
        
        # Obtener eventos disponibles con su tipo de reciclaje
        cursor.execute("""
            SELECT e.id_evento, e.nombre, t.puntos_botella, t.nombre as tipo_reciclaje
            FROM recycling_app.evento e
            JOIN recycling_app.tipo_reciclaje t ON e.id_tipo_reciclaje = t.id_tipo_reciclaje
            ORDER BY e.fecha DESC
        """)
        eventos = cursor.fetchall()
        
        return templates.TemplateResponse(
            "reciclaje/edit.html",
            {
                "request": request, 
                "reciclaje": reciclaje,
                "eventos": eventos
            }
        )
    finally:
        cursor.close()

@router.post("/reciclaje/edit/{id_reciclaje}")
async def edit_reciclaje_submit(
    request: Request,
    id_reciclaje: int,
    current_user: str = Depends(get_current_user),
    id_evento: int = Form(...),
    cantidad: int = Form(...),
    puntos_bono: int = Form(...),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Verificar si es admin
        cursor.execute("""
            SELECT id_perfil 
            FROM recycling_app.usuario 
            WHERE correo = :1
        """, [current_user])
        is_admin = cursor.fetchone()[0] == 2

        # Si no es admin, obtener id_usuario del correo actual
        if not is_admin:
            cursor.execute(
                "SELECT id_usuario FROM recycling_app.usuario WHERE correo = :1",
                [current_user]
            )
            id_usuario = cursor.fetchone()[0]

        # Obtener puntos por botella del tipo de reciclaje del evento
        cursor.execute("""
            SELECT t.puntos_botella
            FROM recycling_app.evento e
            JOIN recycling_app.tipo_reciclaje t ON e.id_tipo_reciclaje = t.id_tipo_reciclaje
            WHERE e.id_evento = :1
        """, [id_evento])
        puntos_botella = cursor.fetchone()[0]

        # Calcular puntos
        puntos = cantidad * puntos_botella
        puntos_totales = puntos + puntos_bono
        
        # Query base para actualizar
        update_query = """
            UPDATE recycling_app.reciclaje 
            SET id_evento = :1,
                cantidad = :2,
                puntos = :3,
                puntos_bono = :4,
                puntos_totales = :5
            WHERE id_reciclaje = :6
        """
        
        # Si no es admin, agregar restricción de usuario
        if not is_admin:
            update_query += " AND id_usuario = :7"
            params = [id_evento, cantidad, puntos, puntos_bono, puntos_totales, id_reciclaje, id_usuario]
        else:
            params = [id_evento, cantidad, puntos, puntos_bono, puntos_totales, id_reciclaje]

        cursor.execute(update_query, params)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reciclaje no encontrado o no tienes permiso para editarlo")
            
        db.commit()
        return RedirectResponse(url="/reciclaje/", status_code=303)
    except Exception as e:
        db.rollback()
        print(f"Error al editar reciclaje: {str(e)}")
        return templates.TemplateResponse(
            "reciclaje/error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )
    finally:
        cursor.close()

@router.delete("/reciclaje/{id_reciclaje}")
async def delete_reciclaje(
    id_reciclaje: int,
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Verificar si es admin
        cursor.execute("""
            SELECT id_perfil 
            FROM recycling_app.usuario 
            WHERE correo = :1
        """, [current_user])
        is_admin = cursor.fetchone()[0] == 2

        if not is_admin:
            # Verificar que el usuario sea el dueño del reciclaje
            cursor.execute("""
                SELECT u.correo
                FROM recycling_app.reciclaje r
                JOIN recycling_app.usuario u ON r.id_usuario = u.id_usuario
                WHERE r.id_reciclaje = :1
            """, [id_reciclaje])
            result = cursor.fetchone()
            
            if not result or result[0] != current_user:
                raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este reciclaje")

        # Primero eliminar registros relacionados en la tabla ranking
        cursor.execute("""
            DELETE FROM recycling_app.ranking 
            WHERE id_reciclaje = :1
        """, [id_reciclaje])

        # Luego eliminar el reciclaje
        cursor.execute("""
            DELETE FROM recycling_app.reciclaje 
            WHERE id_reciclaje = :1
        """, [id_reciclaje])
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reciclaje no encontrado")
            
        db.commit()
        return {"message": "Reciclaje eliminado exitosamente"}
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar reciclaje: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close() 