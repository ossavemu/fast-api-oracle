from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.usuario import UserCreate, UserLogin, User
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..database.connection import get_db
from datetime import timedelta
import oracledb
import re
from pydantic import EmailStr

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    documento: str = Form(...),
    telefono: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: EmailStr = Form(...),
    contrasena: str = Form(...),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Validar formato de teléfono
        if not re.match(r'^3[0-9]{9}$', telefono):
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "error": "El número de teléfono debe ser un celular colombiano válido"
                },
                status_code=400
            )

        # Validar documento
        if not re.match(r'^[0-9]{8,12}$', documento):
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "error": "El documento debe tener entre 8 y 12 números"
                },
                status_code=400
            )

        # Validar nombre y apellido
        if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', nombre) or not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "error": "El nombre y apellido solo pueden contener letras y espacios"
                },
                status_code=400
            )

        # Verificar si el correo ya existe
        cursor.execute(
            "SELECT COUNT(*) FROM recycling_app.usuario WHERE correo = :1",
            [correo]
        )
        if cursor.fetchone()[0] > 0:
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "error": "Este correo ya está registrado"
                },
                status_code=400
            )

        # Verificar si el documento ya existe
        cursor.execute(
            "SELECT COUNT(*) FROM recycling_app.usuario WHERE documento = :1",
            [documento]
        )
        if cursor.fetchone()[0] > 0:
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "error": "Este documento ya está registrado"
                },
                status_code=400
            )

        # Crear usuario
        hashed_password = get_password_hash(contrasena)
        
        cursor.execute("SELECT recycling_app.usuario_seq.NEXTVAL FROM DUAL")
        id_usuario = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO recycling_app.usuario 
            (id_usuario, id_perfil, documento, telefono, nombre, apellido, correo, contrasena)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
        """, [id_usuario, 1, documento, telefono, nombre, apellido, correo, hashed_password])
        
        db.commit()
        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": f"Error al registrar usuario: {str(e)}"
            },
            status_code=500
        )
    finally:
        cursor.close()

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    correo: str = Form(...),
    contrasena: str = Form(...),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT contrasena, id_perfil 
            FROM recycling_app.usuario 
            WHERE correo = :1
        """, [correo])
        result = cursor.fetchone()
        
        if not result or not verify_password(contrasena, result[0]):
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Correo o contraseña incorrectos"}
            )

        is_admin = result[1] == 2
        access_token = create_access_token(
            data={
                "sub": correo,
                "is_admin": is_admin
            }
        )
        
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}")
        
        if is_admin:
            response.set_cookie(key="show_admin_alert", value="true", max_age=5)
            
        return response
    finally:
        cursor.close()

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response