from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..database.connection import get_db
from ..utils.security import get_current_user
import oracledb

router = APIRouter()
templates = Jinja2Templates(directory="app/views/templates")

@router.get("/ranking/", response_class=HTMLResponse)
async def get_ranking(
    request: Request,
    current_user: str = Depends(get_current_user),
    db: oracledb.Connection = Depends(get_db)
):
    cursor = db.cursor()
    try:
        # Obtener ranking general (solo usuarios con puntos)
        cursor.execute("""
            SELECT 
                u.nombre || ' ' || u.apellido as usuario,
                COUNT(r.id_reciclaje) as total_reciclajes,
                SUM(r.puntos_totales) as puntos_totales,
                RANK() OVER (ORDER BY SUM(r.puntos_totales) DESC) as posicion
            FROM recycling_app.usuario u
            JOIN recycling_app.reciclaje r ON u.id_usuario = r.id_usuario
            GROUP BY u.id_usuario, u.nombre, u.apellido
            HAVING SUM(r.puntos_totales) > 0
            ORDER BY puntos_totales DESC
        """)
        ranking_general = cursor.fetchall()

        # Obtener ranking por evento con sus premios
        cursor.execute("""
            WITH RankingEvento AS (
                SELECT 
                    e.id_evento,
                    e.nombre as evento,
                    u.nombre || ' ' || u.apellido as usuario,
                    SUM(r.puntos_totales) as puntos_evento,
                    RANK() OVER (PARTITION BY e.id_evento ORDER BY SUM(r.puntos_totales) DESC) as posicion
                FROM recycling_app.evento e
                JOIN recycling_app.reciclaje r ON e.id_evento = r.id_evento
                JOIN recycling_app.usuario u ON r.id_usuario = u.id_usuario
                GROUP BY e.id_evento, e.nombre, u.id_usuario, u.nombre, u.apellido
                HAVING SUM(r.puntos_totales) > 0
            )
            SELECT 
                re.evento,
                re.usuario,
                re.puntos_evento,
                re.posicion,
                (
                    SELECT LISTAGG(p.descripcion_premio, '; ') WITHIN GROUP (ORDER BY p.id_premio)
                    FROM recycling_app.premio p
                    WHERE p.id_evento = re.id_evento
                ) as premios_evento
            FROM RankingEvento re
            ORDER BY re.id_evento, re.posicion
        """)
        ranking_eventos = cursor.fetchall()

        # Agrupar eventos y sus rankings
        eventos_rankings = {}
        for row in ranking_eventos:
            evento = row[0]
            if evento not in eventos_rankings:
                eventos_rankings[evento] = {
                    'premios': row[4],  # Los premios del evento
                    'participantes': []
                }
            eventos_rankings[evento]['participantes'].append({
                'usuario': row[1],
                'puntos': row[2],
                'posicion': row[3]
            })

        return templates.TemplateResponse(
            "ranking/list.html",
            {
                "request": request,
                "ranking_general": ranking_general,
                "eventos_rankings": eventos_rankings
            }
        )
    finally:
        cursor.close() 