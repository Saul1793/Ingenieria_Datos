#se importan las librerias para realizar el proceso
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os


# Cargar las variables desde .env
load_dotenv()

# Recuperar las variables de entorno
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database_name = os.getenv("DB_NAME")

#una vez listas las variables de entorno se reliza la primera parte de validacion de base de datos

try:
    conn = psycopg2.connect(
        dbname="postgres",  # base de datos por defecto
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
    exists = cursor.fetchone()

    if not exists:
        print(f"Creando base de datos '{database_name}'...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
    else:
        print(f"base de datos '{database_name}' ya existe.")

except Exception as e:
    print("Error en creación de la base de datos:", e)
finally:
    if conn:
        cursor.close()
        conn.close()

#una vez que se creo la base de datos o se valido que existiera se procede a cargar los datos origen a la base de datos


# Paso 2: Conectarse a la base de datos específica para crear la tabla si no existe
try:
    conn = psycopg2.connect(
        dbname=database_name,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS us_origen (
        id SERIAL PRIMARY KEY,
        fisrt_name VARCHAR(100),
        last_name VARCHAR (100),
        company_name VARCHAR (100),
        address VARCHAR (100),
        city VARCHAR (100),
        country VARCHAR (100),
        state VARCHAR (100),
        zip NUMERIC(10,0),
        phone VARCHAR(15),
        phone2 VARCHAR(15),
        email VARCHAR(100),
        web VARCHAR(100)
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    print("La tabla 'empleados' está lista (creada si no existía).")

except Exception as e:
    print("Error en la creación de la tabla:", e)
finally:
    if conn:
        cursor.close()
        conn.close()