from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.bono import Bono
from ..models.premio import Premio
from ..database.connection import get_db
from ..utils.security import get_current_user
import oracledb

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/evento/{id_evento}/bonos", response_class=HTMLResponse)
async def get_evento_bonos(
    request: Request,
    id_evento: int,
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Verificar que el usuario sea el organizador del evento
        cursor.execute("""
            SELECT u.correo
            FROM recycling_app.evento e
            JOIN recycling_app.usuario u ON e.id_usuario = u.id_usuario
            WHERE e.id_evento = :1
        """, [id_evento])
        result = cursor.fetchone()
        is_organizer = result and result[0] == current_user

        # Obtener bonos del evento
        cursor.execute("""
            SELECT id_bono, descripcion, valor_puntos
            FROM recycling_app.bonos
            WHERE id_evento = :1
            ORDER BY valor_puntos DESC
        """, [id_evento])
        bonos = cursor.fetchall()

        # Obtener premios del evento
        cursor.execute("""
            SELECT id_premio, descripcion_premio
            FROM recycling_app.premio
            WHERE id_evento = :1
        """, [id_evento])
        premios = cursor.fetchall()

        return templates.TemplateResponse(
            "evento/bonos.html",
            {
                "request": request,
                "id_evento": id_evento,
                "bonos": bonos,
                "premios": premios,
                "is_organizer": is_organizer
            }
        )
    finally:
        cursor.close()

@router.post("/evento/{id_evento}/bonos")
async def create_bono(
    request: Request,
    id_evento: int,
    descripcion: str = Form(...),
    valor_puntos: int = Form(...),
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Verificar que el usuario sea el organizador
        cursor.execute("""
            SELECT u.correo
            FROM recycling_app.evento e
            JOIN recycling_app.usuario u ON e.id_usuario = u.id_usuario
            WHERE e.id_evento = :1
        """, [id_evento])
        result = cursor.fetchone()
        if not result or result[0] != current_user:
            raise HTTPException(status_code=403, detail="No tienes permiso para crear bonos en este evento")

        # Crear bono
        cursor.execute("SELECT NVL(MAX(id_bono), 0) + 1 FROM recycling_app.bonos")
        id_bono = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO recycling_app.bonos (id_bono, id_evento, descripcion, valor_puntos)
            VALUES (:1, :2, :3, :4)
        """, [id_bono, id_evento, descripcion, valor_puntos])

        db.commit()
        return RedirectResponse(url=f"/evento/{id_evento}/bonos", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.post("/evento/{id_evento}/premios")
async def create_premio(
    request: Request,
    id_evento: int,
    descripcion_premio: str = Form(...),
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Verificar que el usuario sea el organizador
        cursor.execute("""
            SELECT u.correo
            FROM recycling_app.evento e
            JOIN recycling_app.usuario u ON e.id_usuario = u.id_usuario
            WHERE e.id_evento = :1
        """, [id_evento])
        result = cursor.fetchone()
        if not result or result[0] != current_user:
            raise HTTPException(status_code=403, detail="No tienes permiso para crear premios en este evento")

        # Crear premio
        cursor.execute("SELECT NVL(MAX(id_premio), 0) + 1 FROM recycling_app.premio")
        id_premio = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO recycling_app.premio (id_premio, id_evento, descripcion_premio)
            VALUES (:1, :2, :3)
        """, [id_premio, id_evento, descripcion_premio])

        db.commit()
        return RedirectResponse(url=f"/evento/{id_evento}/bonos", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close() 