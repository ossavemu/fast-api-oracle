-- Crear usuario y otorgar permisos
ALTER SESSION SET "_ORACLE_SCRIPT"=true;
CREATE USER recycling_app IDENTIFIED BY "password123";
GRANT ALL PRIVILEGES TO recycling_app;
GRANT UNLIMITED TABLESPACE TO recycling_app;
GRANT CREATE SESSION TO recycling_app;
GRANT CREATE TABLE TO recycling_app;
GRANT CREATE SEQUENCE TO recycling_app;
GRANT CREATE VIEW TO recycling_app;

-- Conectar como el usuario recycling_app
CONNECT recycling_app/password123@//localhost:1521/XE

-- Establecer el esquema actual
ALTER SESSION SET CURRENT_SCHEMA = recycling_app; 