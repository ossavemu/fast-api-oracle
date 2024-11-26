from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.evento import Evento
from ..database.connection import get_db
from ..utils.security import get_current_user
from datetime import datetime
import oracledb

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/evento/", response_class=HTMLResponse)
async def get_eventos(
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
                e.*,
                u.nombre || ' ' || u.apellido as organizador,
                t.nombre as tipo_reciclaje,
                u.correo as email_organizador,
                (
                    SELECT COUNT(*)
                    FROM recycling_app.bonos b
                    WHERE b.id_evento = e.id_evento
                ) as total_bonos,
                (
                    SELECT COUNT(*)
                    FROM recycling_app.premio p
                    WHERE p.id_evento = e.id_evento
                ) as total_premios,
                COALESCE(
                    (
                        SELECT SUM(b.valor_puntos)
                        FROM recycling_app.bonos b
                        WHERE b.id_evento = e.id_evento
                    ), 0
                ) as total_puntos_bonos
            FROM recycling_app.evento e
            JOIN recycling_app.usuario u ON e.id_usuario = u.id_usuario
            JOIN recycling_app.tipo_reciclaje t ON e.id_tipo_reciclaje = t.id_tipo_reciclaje
            ORDER BY e.fecha DESC
        """)
        eventos = cursor.fetchall()
        return templates.TemplateResponse(
            "evento/list.html",
            {
                "request": request, 
                "eventos": eventos, 
                "current_user": current_user,
                "is_admin": is_admin
            }
        )
    finally:
        cursor.close()

@router.get("/evento/create", response_class=HTMLResponse)
async def create_evento_form(
    request: Request,
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Obtener tipos de reciclaje disponibles
        cursor.execute("""
            SELECT id_tipo_reciclaje, nombre, caracteristicas, puntos_botella
            FROM recycling_app.tipo_reciclaje
            ORDER BY nombre
        """)
        tipos_reciclaje = cursor.fetchall()
        
        return templates.TemplateResponse(
            "evento/create.html",
            {"request": request, "tipos_reciclaje": tipos_reciclaje}
        )
    finally:
        cursor.close()

@router.get("/evento/{id_evento}", response_class=HTMLResponse)
async def get_evento_detail(
    request: Request,
    id_evento: int,
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Obtener detalles del evento
        cursor.execute("""
            SELECT e.*, u.nombre || ' ' || u.apellido as organizador,
                   t.nombre as tipo_reciclaje, t.puntos_botella
            FROM recycling_app.evento e
            JOIN recycling_app.usuario u ON e.id_usuario = u.id_usuario
            JOIN recycling_app.tipo_reciclaje t ON e.id_tipo_reciclaje = t.id_tipo_reciclaje
            WHERE e.id_evento = :1
        """, [id_evento])
        evento = cursor.fetchone()
        
        if not evento:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        # Obtener estadísticas del evento
        cursor.execute("""
            SELECT COUNT(*) as total_reciclajes,
                   SUM(cantidad) as total_items,
                   SUM(puntos_totales) as total_puntos
            FROM recycling_app.reciclaje
            WHERE id_evento = :1
        """, [id_evento])
        stats = cursor.fetchone()

        # Obtener participantes del evento
        cursor.execute("""
            SELECT DISTINCT u.nombre || ' ' || u.apellido as participante,
                   COUNT(r.id_reciclaje) as reciclajes,
                   SUM(r.puntos_totales) as puntos
            FROM recycling_app.usuario u
            JOIN recycling_app.reciclaje r ON u.id_usuario = r.id_usuario
            WHERE r.id_evento = :1
            GROUP BY u.nombre, u.apellido
            ORDER BY puntos DESC
        """, [id_evento])
        participantes = cursor.fetchall()

        # Obtener bonos del evento
        cursor.execute("""
            SELECT id_bono, descripcion, valor_puntos
            FROM recycling_app.bonos
            WHERE id_evento = :1
            ORDER BY valor_puntos DESC
            FETCH FIRST 3 ROWS ONLY
        """, [id_evento])
        bonos = cursor.fetchall()

        return templates.TemplateResponse(
            "evento/detail.html",
            {
                "request": request,
                "evento": evento,
                "stats": stats,
                "participantes": participantes,
                "current_user": current_user,
                "bonos": bonos
            }
        )
    finally:
        cursor.close()

@router.get("/evento/edit/{id_evento}", response_class=HTMLResponse)
async def edit_evento_form(
    request: Request,
    id_evento: int,
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

        # Obtener evento y organizador
        cursor.execute("""
            SELECT e.*, u.correo
            FROM recycling_app.evento e
            JOIN recycling_app.usuario u ON e.id_usuario = u.id_usuario
            WHERE e.id_evento = :1
        """, [id_evento])
        evento = cursor.fetchone()
        
        if not evento:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
            
        # Permitir edición solo al organizador o admin
        if not is_admin and evento[-1] != current_user:
            raise HTTPException(status_code=403, detail="No tienes permiso para editar este evento")

        # Obtener tipos de reciclaje
        cursor.execute("""
            SELECT id_tipo_reciclaje, nombre, caracteristicas, puntos_botella
            FROM recycling_app.tipo_reciclaje
            ORDER BY nombre
        """)
        tipos_reciclaje = cursor.fetchall()

        # Obtener bonos existentes
        cursor.execute("""
            SELECT id_bono, descripcion, valor_puntos
            FROM recycling_app.bonos
            WHERE id_evento = :1
            ORDER BY valor_puntos DESC
        """, [id_evento])
        bonos = cursor.fetchall()

        # Obtener premios existentes
        cursor.execute("""
            SELECT id_premio, descripcion_premio
            FROM recycling_app.premio
            WHERE id_evento = :1
        """, [id_evento])
        premios = cursor.fetchall()

        return templates.TemplateResponse(
            "evento/create.html",  # Usamos el mismo template para crear/editar
            {
                "request": request,
                "evento": evento,
                "tipos_reciclaje": tipos_reciclaje,
                "bonos": bonos,
                "premios": premios
            }
        )
    finally:
        cursor.close()

@router.post("/evento/edit/{id_evento}")
async def edit_evento_submit(
    request: Request,
    id_evento: int,
    current_user: str = Depends(get_current_user),
    nombre: str = Form(...),
    lugar: str = Form(...),
    fecha: str = Form(...),
    h_inicio: str = Form(...),
    h_final: str = Form(...),
    id_tipo_reciclaje: int = Form(...),
    observaciones: str = Form(None),
    bono_descripcion: list[str] = Form([]),
    bono_valor: list[int] = Form([]),
    premio_descripcion: list[str] = Form([]),
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
            raise HTTPException(status_code=403, detail="No tienes permiso para editar este evento")

        # Combinar fecha y hora
        fecha_inicio = f"{fecha} {h_inicio}"
        fecha_final = f"{fecha} {h_final}"

        # Actualizar evento
        cursor.execute("""
            UPDATE recycling_app.evento 
            SET nombre = :1,
                lugar = :2,
                h_inicio = :3,
                h_final = :4,
                fecha = :5,
                id_tipo_reciclaje = :6,
                observaciones = :7
            WHERE id_evento = :8
        """, [
            nombre, lugar,
            datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M'),
            datetime.strptime(fecha_final, '%Y-%m-%d %H:%M'),
            datetime.strptime(fecha, '%Y-%m-%d'),
            id_tipo_reciclaje,
            observaciones,
            id_evento
        ])
        
        # Eliminar bonos y premios existentes
        cursor.execute("DELETE FROM recycling_app.bonos WHERE id_evento = :1", [id_evento])
        cursor.execute("DELETE FROM recycling_app.premio WHERE id_evento = :1", [id_evento])

        # Insertar nuevos bonos
        for desc, valor in zip(bono_descripcion, bono_valor):
            if desc.strip() and valor > 0:
                cursor.execute("""
                    INSERT INTO recycling_app.bonos (id_bono, id_evento, descripcion, valor_puntos)
                    VALUES (recycling_app.bonos_seq.NEXTVAL, :1, :2, :3)
                """, [id_evento, desc.strip(), valor])

        # Insertar nuevos premios
        for desc in premio_descripcion:
            if desc.strip():
                cursor.execute("""
                    INSERT INTO recycling_app.premio (id_premio, id_evento, descripcion_premio)
                    VALUES (recycling_app.premio_seq.NEXTVAL, :1, :2)
                """, [id_evento, desc.strip()])
        
        db.commit()
        return RedirectResponse(url=f"/evento/{id_evento}", status_code=303)
    except Exception as e:
        db.rollback()
        print(f"Error al editar evento: {str(e)}")  # Log para debug
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.post("/evento/create")
async def create_evento(
    request: Request,
    current_user: str = Depends(get_current_user),
    nombre: str = Form(...),
    lugar: str = Form(...),
    fecha: str = Form(...),
    h_inicio: str = Form(...),
    h_final: str = Form(...),
    id_tipo_reciclaje: int = Form(...),
    observaciones: str = Form(None),
    bono_descripcion: list = Form([]),
    bono_valor: list = Form([]),
    premio_descripcion: list = Form([]),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Obtener id_usuario del correo actual
        cursor.execute(
            "SELECT id_usuario FROM recycling_app.usuario WHERE correo = :1",
            [current_user]
        )
        result = cursor.fetchone()
        if not result:
            return templates.TemplateResponse(
                "evento/error.html",
                {
                    "request": request,
                    "error": "Usuario no encontrado en el sistema"
                },
                status_code=404
            )

        id_usuario = result[0]

        # Validar fecha y hora
        try:
            fecha_inicio = f"{fecha} {h_inicio}"
            fecha_final = f"{fecha} {h_final}"
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M')
            fecha_final_dt = datetime.strptime(fecha_final, '%Y-%m-%d %H:%M')
            
            if fecha_inicio_dt >= fecha_final_dt:
                return templates.TemplateResponse(
                    "evento/error.html",
                    {
                        "request": request,
                        "error": "La hora de inicio debe ser anterior a la hora final"
                    },
                    status_code=400
                )
        except ValueError:
            return templates.TemplateResponse(
                "evento/error.html",
                {
                    "request": request,
                    "error": "Formato de fecha u hora inválido"
                },
                status_code=400
            )

        # Obtener siguiente ID
        cursor.execute("SELECT NVL(MAX(id_evento), 0) + 1 FROM recycling_app.evento")
        id_evento = cursor.fetchone()[0]

        try:
            # Insertar evento
            cursor.execute("""
                INSERT INTO recycling_app.evento 
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
            """, [
                id_evento, id_usuario, id_tipo_reciclaje, nombre, lugar,
                fecha_inicio_dt,
                fecha_final_dt,
                datetime.strptime(fecha, '%Y-%m-%d'),
                observaciones
            ])

            # Insertar bonos si existen
            if bono_descripcion and bono_valor and len(bono_descripcion) == len(bono_valor):
                for desc, valor in zip(bono_descripcion, bono_valor):
                    if desc and valor:  # Verificar que ambos valores existan
                        try:
                            cursor.execute("""
                                INSERT INTO recycling_app.bonos (id_bono, id_evento, descripcion, valor_puntos)
                                VALUES (recycling_app.bonos_seq.NEXTVAL, :1, :2, :3)
                            """, [id_evento, desc.strip(), int(valor)])
                        except Exception as e:
                            print(f"Error al insertar bono: {str(e)}")
                            continue

            # Insertar premios si existen
            if premio_descripcion:
                for desc in premio_descripcion:
                    if desc:  # Verificar que la descripción exista
                        try:
                            cursor.execute("""
                                INSERT INTO recycling_app.premio (id_premio, id_evento, descripcion_premio)
                                VALUES (recycling_app.premio_seq.NEXTVAL, :1, :2)
                            """, [id_evento, desc.strip()])
                        except Exception as e:
                            print(f"Error al insertar premio: {str(e)}")
                            continue

            db.commit()
            return RedirectResponse(url="/evento/", status_code=303)
        except Exception as e:
            db.rollback()
            error_msg = str(e)
            if "ORA-00001" in error_msg:
                error_msg = "Ya existe un evento con ese nombre"
            elif "ORA-02290" in error_msg:
                error_msg = "Uno o más valores ingresados no son válidos"
            
            return templates.TemplateResponse(
                "evento/error.html",
                {
                    "request": request,
                    "error": f"Error al crear el evento: {error_msg}"
                },
                status_code=500
            )

    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "evento/error.html",
            {
                "request": request,
                "error": f"Error inesperado: {str(e)}"
            },
            status_code=500
        )
    finally:
        cursor.close()

@router.delete("/evento/{id_evento}")
async def delete_evento(
    id_evento: int,
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
            # Verificar que el usuario sea el organizador
            cursor.execute("""
                SELECT u.correo
                FROM recycling_app.evento e
                JOIN recycling_app.usuario u ON e.id_usuario = u.id_usuario
                WHERE e.id_evento = :1
            """, [id_evento])
            result = cursor.fetchone()
            
            if not result or result[0] != current_user:
                raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este evento")

        # Si es admin, puede eliminar aunque tenga reciclajes
        if not is_admin:
            # Verificar si hay reciclajes asociados
            cursor.execute("""
                SELECT COUNT(*) FROM recycling_app.reciclaje WHERE id_evento = :1
            """, [id_evento])
            if cursor.fetchone()[0] > 0:
                raise HTTPException(
                    status_code=400, 
                    detail="No se puede eliminar el evento porque tiene reciclajes asociados"
                )

        # Eliminar bonos y premios primero
        cursor.execute("DELETE FROM recycling_app.bonos WHERE id_evento = :1", [id_evento])
        cursor.execute("DELETE FROM recycling_app.premio WHERE id_evento = :1", [id_evento])

        # Si es admin, eliminar reciclajes asociados
        if is_admin:
            cursor.execute("DELETE FROM recycling_app.reciclaje WHERE id_evento = :1", [id_evento])

        # Eliminar evento
        cursor.execute("""
            DELETE FROM recycling_app.evento WHERE id_evento = :1
        """, [id_evento])
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
            
        db.commit()
        return {"message": "Evento eliminado exitosamente"}
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar evento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/api/evento/{id_evento}/bonos")
async def get_evento_bonos(
    id_evento: int,
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT id_bono, descripcion, valor_puntos
            FROM recycling_app.bonos
            WHERE id_evento = :1
            ORDER BY valor_puntos DESC
        """, [id_evento])
        
        bonos = []
        for row in cursor.fetchall():
            bonos.append({
                "id_bono": row[0],
                "descripcion": row[1],
                "valor_puntos": row[2]
            })
            
        return bonos
    finally:
        cursor.close() 