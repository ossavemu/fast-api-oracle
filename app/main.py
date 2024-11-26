from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .controllers import reciclaje_controller, auth_controller, evento_controller, ranking_controller, evento_bonos_controller, tipo_reciclaje_controller
from .utils.security import get_current_user
from .middleware.admin import add_admin_status
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

# Agregar middleware de admin
app.add_middleware(BaseHTTPMiddleware, dispatch=add_admin_status)

app.mount("/static", StaticFiles(directory="app/views/static"), name="static")
templates = Jinja2Templates(directory="app/views/templates")

# Incluir rutas
app.include_router(auth_controller.router)
app.include_router(
    reciclaje_controller.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    evento_controller.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    ranking_controller.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    evento_bonos_controller.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    tipo_reciclaje_controller.router,
    tags=["materiales"],
    dependencies=[Depends(get_current_user)]
)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Obtener el estado de admin del request
    is_admin = getattr(request.state, 'is_admin', False)
    return templates.TemplateResponse(
        "landing.html", 
        {
            "request": request,
            "is_admin": is_admin
        }
    ) 