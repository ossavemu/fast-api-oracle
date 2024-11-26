FROM container-registry.oracle.com/database/express:21.3.0-xe

# Variables de entorno
ENV ORACLE_PWD=oracle123
ENV ORACLE_CHARACTERSET=AL32UTF8
ENV NLS_LANG=AMERICAN_AMERICA.AL32UTF8

# Copiar scripts SQL
COPY setup.sql /opt/oracle/scripts/startup/01_setup.sql
COPY base_datos.sql /opt/oracle/scripts/startup/02_create_tables.sql

# Puerto por defecto de Oracle
EXPOSE 1521 