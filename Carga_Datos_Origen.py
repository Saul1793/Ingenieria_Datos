#para este ejemplo se usa pandas al ser pocos registros se puede usar polars para hacer uso de lacy frames o pyspark
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Conexión a la base de datos
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database_name = os.getenv("DB_NAME")

# Ruta al archivo CSV
csv_file = os.getenv("RUTA")

# Leer el CSV con pandas
try:
    # Puedes ajustar encoding si te da error (utf-8, latin-1, etc.)
    df = pd.read_csv(csv_file, encoding="utf-8")
    print("Datos cargados desde el CSV:")
    print(df.head())
except Exception as e:
    print("Error leyendo el CSV:", e)
    exit(1)

# Conexión a la base de datos para insertar los datos
try:
    conn = psycopg2.connect(
        dbname=database_name,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = conn.cursor()

    # Recorrer el DataFrame e insertar fila por fila
    for index, row in df.iterrows():
        cursor.execute("""
                INSERT INTO us_origen (
                    fisrt_name, last_name, company_name, address, city,
                    country, state, zip, phone, phone2, email, web
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
            row['first_name'],
            row['last_name'],
            row['company_name'],
            row['address'],
            row['city'],
            row['county'],
            row['state'],
            row['zip'],
            row['phone1'],
            row['phone2'],
            row['email'],
            row['web']
        ))

    conn.commit()
    print(f"Datos insertados correctamente en la tabla us_origen .")

except Exception as e:
    print("Error insertando datos:", e)
finally:
    if conn:
        cursor.close()
        conn.close()
