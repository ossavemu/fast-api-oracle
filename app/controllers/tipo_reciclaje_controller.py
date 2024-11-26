from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..database.connection import get_db
from ..utils.security import get_current_user
import oracledb

router = APIRouter(prefix="/materiales")
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/", response_class=HTMLResponse)
async def get_materiales(
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

        if not is_admin:
            raise HTTPException(status_code=403, detail="Acceso no autorizado")

        cursor.execute("""
            SELECT id_tipo_reciclaje, nombre, caracteristicas, puntos_botella
            FROM recycling_app.tipo_reciclaje
            ORDER BY nombre
        """)
        materiales = cursor.fetchall()

        return templates.TemplateResponse(
            "materiales/list.html",
            {
                "request": request, 
                "materiales": materiales,
                "is_admin": is_admin
            }
        )
    finally:
        cursor.close()

@router.post("/create")
async def create_material(
    request: Request,
    current_user: str = Depends(get_current_user),
    nombre: str = Form(...),
    caracteristicas: str = Form(...),
    puntos_botella: int = Form(...),
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
            raise HTTPException(status_code=403, detail="Acceso no autorizado")

        cursor.execute("""
            INSERT INTO recycling_app.tipo_reciclaje 
            (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
            VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, :1, :2, :3)
        """, [nombre, caracteristicas, puntos_botella])

        db.commit()
        return RedirectResponse(url="/materiales/", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close() 

@router.get("/edit/{id_material}", response_class=HTMLResponse)
async def edit_material_form(
    request: Request,
    id_material: int,
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
            raise HTTPException(status_code=403, detail="Acceso no autorizado")

        cursor.execute("""
            SELECT id_tipo_reciclaje, nombre, caracteristicas, puntos_botella
            FROM recycling_app.tipo_reciclaje
            WHERE id_tipo_reciclaje = :1
        """, [id_material])
        material = cursor.fetchone()

        if not material:
            raise HTTPException(status_code=404, detail="Material no encontrado")

        return templates.TemplateResponse(
            "materiales/edit.html",
            {"request": request, "material": material}
        )
    finally:
        cursor.close()

@router.post("/edit/{id_material}")
async def edit_material(
    request: Request,
    id_material: int,
    current_user: str = Depends(get_current_user),
    nombre: str = Form(...),
    caracteristicas: str = Form(...),
    puntos_botella: int = Form(...),
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
            raise HTTPException(status_code=403, detail="Acceso no autorizado")

        cursor.execute("""
            UPDATE recycling_app.tipo_reciclaje 
            SET nombre = :1,
                caracteristicas = :2,
                puntos_botella = :3
            WHERE id_tipo_reciclaje = :4
        """, [nombre, caracteristicas, puntos_botella, id_material])

        db.commit()
        return RedirectResponse(url="/materiales/", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.delete("/{id_material}")
async def delete_material(
    id_material: int,
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
            raise HTTPException(status_code=403, detail="Acceso no autorizado")

        # Verificar si hay eventos usando este material
        cursor.execute("""
            SELECT COUNT(*) FROM recycling_app.evento 
            WHERE id_tipo_reciclaje = :1
        """, [id_material])
        
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el material porque está siendo usado en eventos"
            )

        cursor.execute("""
            DELETE FROM recycling_app.tipo_reciclaje 
            WHERE id_tipo_reciclaje = :1
        """, [id_material])

        db.commit()
        return {"message": "Material eliminado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close() 