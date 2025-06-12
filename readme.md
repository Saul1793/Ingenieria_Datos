###  `README.md`

````markdown
# Sistema de Carga de Datos a AWS (Redshift) con JARs y Scripts Locales

Este proyecto permite ejecutar una carga de datos desde una base local hasta AWS Redshift, utilizando scripts Python, conectores `.jar`, y herramientas como Java y WinUtils para entornos Windows.

---

## Requisitos del Sistema

Antes de comenzar, asegúrate de tener lo siguiente instalado:

### Python

- Python **3.11**

Crea un entorno virtual y actívalo:

```bash
python -m venv .venv
.\.venv\Scripts\activate
````

---

### Java

* Instala **Java 8** (versión 1.8.x)
* Asegúrate de que la variable de entorno `JAVA_HOME` apunte correctamente a la carpeta de instalación.

---

### Archivos `.jar`

En el presente repositorio se incluyen los archivos `.jar` necesarios:

* Conectores a bases de datos (por ejemplo, PostgreSQL, Redshift, etc.)
* Archivos requeridos por Spark u otros procesos si aplica

Guárdalos en la carpeta indicada dentro del proyecto.

---

### WinUtils (para entornos Windows)

* Descarga **WinUtils v3** desde GitHub.
* Guarda los ejecutables en la carpeta correspondiente del proyecto.
* Asegúrate de que las variables de entorno están correctamente configuradas para apuntar a los binarios de WinUtils.

---

## Configuración del Proyecto

1. **Configura el archivo `.env`** con tus credenciales y rutas. Usa `.env.example` como referencia si está disponible.

---

##  Ejecución del Sistema

Sigue este orden para ejecutar los scripts correctamente:

1. **Configurar el archivo `.env`** con las variables necesarias.
2. Ejecutar el script:

   ```bash
   python creacion_base_tabla.py
   ```
3. Ejecutar el script de carga desde el origen:

   ```bash
   python carga_datos_origen.py
   ```
4. Configura tu acceso a **AWS** (ya sea en el `.env` o con AWS CLI).
5. Ejecuta el script de carga hacia AWS:

   ```bash
   python carga_datos_aws.py
   ```

---

## Estructura Sugerida del Proyecto

```
📦 tu-proyecto/
├── creacion_base_tabla.py
├── carga_datos_origen.py
├── carga_datos_aws.py
├── .env
├── .env.example
├── jars/
│   └── *.jar
├── winutils/
│   └── winutils.exe
├── requirements.txt
└── README.md
```

---

## Notas

* Asegúrate de tener permisos y configuraciones correctas para acceder a bases de datos y servicios de AWS.
* Este sistema está diseñado para ejecutarse en entornos locales con soporte para Java y herramientas de línea de comandos.
