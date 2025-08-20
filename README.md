# EcoMont - Sistema de Gestión de Residuos

## Configuración de la Base de Datos

1. Instalar PostgreSQL en tu PC.
2. Crear la base de datos llamada `ecomont`.
3. Abrir pgAdmin, conectarte a la BD `ecomont`.
4. Abrir y ejecutar el archivo `db/schema.sql`.
5. (Opcional) Ejecutar `db/data.sql` si querés datos de ejemplo.

## Requisitos de Python

- Flask
- psycopg2-binary

Instalar con:

```bash
pip install -r requirements.txt






🗃️ Gestión de la Base de Datos – EcoMont

Este proyecto permite trabajar con la base de datos de dos formas distintas:
        Usando SQL puro directamente en PostgreSQL
        Usando modelos Python con Flask y SQLAlchemy



✅ Opción 1: Trabajar directamente con PostgreSQL (modo manual)
Podés usar pgAdmin o la consola psql para ejecutar comandos SQL directamente sobre la base de datos.
    Herramientas recomendadas:
            pgAdmin: interfaz visual para administrar PostgreSQL.
            psql: consola de comandos de PostgreSQL.

Archivos disponibles:
            db/schema.sql: crea las tablas necesarias para el sistema.
            db/data.sql: inserta datos de ejemplo (usuarios, reportes, etc.).

Instrucciones desde la consola:
        psql -U postgres -d ecomont

Una vez dentro de psql, ejecutá:
            \i db/schema.sql
            \i db/data.sql




✅ Opción 2: Trabajar desde Python (modo automático con Flask)
Usamos los modelos definidos con SQLAlchemy (db.Model) para crear y manipular las tablas desde código.

    Archivos:
            init_db.py: crea todas las tablas automáticamente desde los modelos.
            init_data.py: carga datos de ejemplo desde Python (en lugar de data.sql).

    Instrucciones:
            python init_db.py     # Crea las tablas
            data.py   # Carga datos iniciales

⚠️ Asegurate de tener correctamente configurada la base de datos en app.py.





📦 ¿Qué archivos conservar y para qué?


schema.sql       Crear tablas con SQL puro, usarlo desde pgAdmin o psql
data.sql         Insertar datos con SQL puro, usarlo  desde pgAdmin o psql
init_db.py       Crear tablas desde modelos en Python, usarlo si usás Flask y SQLAlchemy
init_data.py     Insertar datos desde Python, usarlo cuando hacemos pruebas sin escribir SQL puro



ℹ️ Notas importantes

Podés usar la opción que prefieras, ambas generan y manejan la misma base.
       > Si trabajás con modelos Python (ReporteCiudadano, etc.), es más práctico usar init_db.py y init_data.py.

       > Si solo querés hacer pruebas rápidas o tenés errores con Python, podés usar schema.sql y data.sql directamente en pgAdmin.

📂 Estructura recomendada del proyecto

EcoMont/
├── app.py                # Aplicación principal Flask
├── init_db.py            # Crea tablas desde modelos SQLAlchemy
├── init_data.py          # Inserta datos de ejemplo desde Python
├── db/
│   ├── schema.sql        # Script SQL para crear tablas (manual)
│   └── data.sql          # Script SQL para insertar datos (manual)
├── templates/            # HTML con Jinja2
├── static/               # Archivos estáticos (CSS, imágenes, JS)
├── requirements.txt      # Dependencias del proyecto
└── README.md             # Instrucciones y guía del proyecto