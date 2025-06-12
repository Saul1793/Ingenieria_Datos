import os
import sys
import threading
import boto3
from boto3.s3.transfer import TransferConfig
from pyspark.sql import SparkSession
from dotenv import load_dotenv
from botocore.config import Config

load_dotenv()

#Configuración inicial
os.environ["HADOOP_HOME"] = os.getenv("HADOOP_HOME_PATH")
os.environ["PYSPARK_PYTHON"] = os.getenv("PYTHON_PATH")

#AWS Config
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "prueba-tecnica-saul"
PARQUET_DIR = "us_origen_output"  # Directorio para los archivos Parquet
S3_PATH = "output_parquet/us_origen_output"  # Ruta en S3

# Crear sesion de SparkSession
jar_path = (
    f"""file:///{ os.getenv("JAR_PATH_POSTGRESQL")},"""
    f"""file:///{ os.getenv("JAR_PATH_REDSHIFT_DB")}"""
)

spark = SparkSession.builder \
    .appName("ETL PostgreSQL Redshift") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.hadoop.hadoop.native.lib", "false") \
    .config("spark.jars", jar_path) \
    .getOrCreate()

# Extracción de PostgreSQL
pg_url = f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
pg_properties = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "driver": "org.postgresql.Driver"
}

print("Leyendo datos desde PostgreSQL...")
df_pg = spark.read \
    .format("jdbc") \
    .option("url", pg_url) \
    .option("dbtable", '"us_origen"') \
    .option("user", pg_properties["user"]) \
    .option("password", pg_properties["password"]) \
    .option("driver", pg_properties["driver"]) \
    .load()

#se hace un llamado a los datos para visualizar que se cargaron realmente
print("Datos leídos desde PostgreSQL:")
df_pg.show(5)

# Carga a Redshift
print("⚡ Cargando datos a Redshift...")
redshift_url = f"jdbc:redshift://{os.getenv('REDSHIFT_HOST')}:{os.getenv('REDSHIFT_PORT')}/{os.getenv('REDSHIFT_DB')}"
redshift_properties = {
    "user": os.getenv("REDSHIFT_USER"),
    "password": os.getenv("REDSHIFT_PASSWORD"),
    "driver": "com.amazon.redshift.jdbc42.Driver"
}

df_pg.write \
    .format("jdbc") \
    .option("url", redshift_url) \
    .option("dbtable", "us_origen") \
    .option("user", redshift_properties["user"]) \
    .option("password", redshift_properties["password"]) \
    .option("driver", redshift_properties["driver"]) \
    .option("ssl", "true") \
    .mode("overwrite") \
    .save()

print("Datos cargados exitosamente a Redshift!")

# Se Guardar como Parquet local
print(f"Guardando Parquet en {os.path.abspath(PARQUET_DIR)}...")
df_pg.write.mode("overwrite").parquet(PARQUET_DIR)
print(f"Parquet guardado localmente en: {os.path.abspath(PARQUET_DIR)}")

# Configuración S3
s3_config = Config(
    retries={'max_attempts': 3, 'mode': 'standard'},
    signature_version='s3v4'
)

#se instancia la variable boto3 para crear la conexión de forma correcta
s3 = boto3.resource(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    config=s3_config
)


# Función para subir directorio a S3
def upload_directory_to_s3(bucket_name, s3_path, local_path):
    for root, _, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_path)
            s3_file_path = os.path.join(s3_path, relative_path).replace("\\", "/")

            # Configuración de transferencia con callback
            file_size = os.path.getsize(local_file_path)
            callback = TransferCallback(file_size)
            transfer_config = TransferConfig(
                multipart_threshold=8 * 1024 * 1024,  # 8MB
                max_concurrency=10
            )

            print(f"\n Subiendo {file} ({file_size / 1024 / 1024:.2f} MB)...")
            s3.Bucket(bucket_name).upload_file(
                local_file_path,
                s3_file_path,
                Config=transfer_config,
                Callback=callback
            )
    print("\n Todos los archivos subidos!")


class TransferCallback:
    def __init__(self, target_size):
        self._target_size = target_size
        self._transferred = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_transferred):
        with self._lock:
            self._transferred += bytes_transferred
            percent = (self._transferred / self._target_size) * 100
            sys.stdout.write(f"\rProgreso: {percent:.2f}% ({self._transferred} bytes)")
            sys.stdout.flush()


# Ejecutar la subida a S3
print("\n Iniciando subida a S3...")
upload_directory_to_s3(
    bucket_name=BUCKET_NAME,
    s3_path=S3_PATH,
    local_path=PARQUET_DIR
)

# se detiene la sesion de spark despues de subir los datos
spark.stop()
print(" Proceso completado exitosamente!")