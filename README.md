
# Proyecto de Reciclaje - Instalación en Local (Windows)

## Requisitos previos

1. **Instalar Python 3.8 o superior**:  
   [Descargar Python](https://www.python.org/downloads/)
2. **Instalar Docker y Docker Compose**:  
   [Descargar Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## Instalación y configuración del proyecto

### 1. Clonar el repositorio
Abre la terminal y clona el repositorio del proyecto:
```bash
git clone https://github.com/ossavemu/fast-api-oracle.git
cd fast-api-oracle
```

### 2. Configurar el entorno virtual de Python
Crea y activa el entorno virtual:
```bash
python -m venv venv
```

**Activar el entorno virtual**:
- En PowerShell:
  ```bash
  .\venv\Scripts\Activate.ps1
  ```
- En CMD:
  ```bash
  venv\Scripts\activate
  ```

### 3. Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos Oracle con Docker
Inicia los contenedores Docker:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 5. Ejecutar los scripts SQL
**Espera 2 minutos para que la base de datos se inicialice.**

Luego, ejecuta los siguientes comandos uno por uno en la terminal:

```bash
# Ejecutar setup.sql
docker exec -it basesoracle-oracle-db-1 sqlplus sys/oracle123@//localhost:1521/XE as sysdba "@/opt/oracle/scripts/startup/01_setup.sql"

# Ejecutar base_datos.sql
docker exec -it basesoracle-oracle-db-1 sqlplus recycling_app/password123@//localhost:1521/XE "@/opt/oracle/scripts/startup/02_create_tables.sql"

# Copiar y ejecutar pruebas.sql
docker cp pruebas.sql basesoracle-oracle-db-1:/opt/oracle/pruebas.sql
docker exec -it basesoracle-oracle-db-1 sqlplus recycling_app/password123@//localhost:1521/XE "@/opt/oracle/pruebas.sql"
```

### 6. Ejecutar la aplicación FastAPI
Asegúrate de que el entorno virtual está activado, luego ejecuta:
```bash
uvicorn app.main:app --reload
```

### 7. Acceder a la aplicación
Abre el navegador y visita:
```
http://localhost:8000
```

---

## Comandos útiles

**Ver logs de Docker:**
```bash
docker-compose logs -f
```

**Abrir consola SQL de Oracle:**
```bash
docker exec -it basesoracle-oracle-db-1 sqlplus recycling_app/password123@//localhost:1521/XE
```

---

## Credenciales de superusuario
- **Email:** sudo@admin.com
- **Contraseña:** ADMIN2024

