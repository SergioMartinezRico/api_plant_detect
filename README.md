# AgroDetect API v2 (Backend)

Este repositorio contiene el backend de **AgroDetect**, un servicio diseñado para el análisis biológico de plantas mediante procesamiento de imágenes. Actúa como un middleware inteligente que conecta aplicaciones cliente (drones, apps móviles) con el motor de identificación `Plant.id`.

El sistema es capaz de realizar identificación taxonómica, evaluación de salud y detección de patologías con sugerencias de tratamiento.

## Características

- **API RESTful:** Construida sobre Flask.
- **Análisis Dual:** Soporta ingesta de imágenes tanto por URL pública como por Base64.
- **Motor PlantBioEngine:** Capa de abstracción que normaliza la respuesta de proveedores externos.
- **Diagnóstico de Salud:** Detección de enfermedades, probabilidad de riesgo y sugerencias de tratamiento (químico, biológico y preventivo).
- **Modo Demo:** Actualmente configurado para análisis global (geolocalización desactivada intencionalmente para pruebas genéricas).

## Requisitos Previos

- Python 3.8+
- Una API Key válida de [Plant.id](https://web.plant.id/).

## Instalación

1. Clonar el repositorio:
    ```bash
    git clone <url-del-repo>
    cd agrodetect-backend
    ```

2. Crear un entorno virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. Instalar dependencias:
    ```bash
    pip install flask flask-cors python-dotenv requests
    ```

## Configuración

El sistema requiere variables de entorno para funcionar. Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:


# API Key obligatoria para el motor de reconocimiento
PLANT_ID_API_KEY=tu_api_key_aqui

# AgroDetect API v2 (Backend)

Este repositorio contiene el backend de **AgroDetect**, un servicio diseñado para el análisis biológico de plantas mediante procesamiento de imágenes. Actúa como un middleware inteligente que conecta aplicaciones cliente (drones, apps móviles) con el motor de identificación Plant.id.

El sistema es capaz de realizar identificación taxonómica, evaluación de salud y detección de patologías con sugerencias de tratamiento.

## Características

- API RESTful: Construida sobre Flask.
- Análisis Dual: Soporta ingesta de imágenes tanto por URL pública como por Base64.
- Motor PlantBioEngine: Capa de abstracción que normaliza la respuesta de proveedores externos.
- Diagnóstico de Salud: Detección de enfermedades, probabilidad de riesgo y sugerencias de tratamiento (químico, biológico y preventivo).
- Modo Demo: Actualmente configurado para análisis global (geolocalización desactivada intencionalmente para pruebas genéricas).

## Requisitos Previos

- Python 3.8+
- Una API Key válida de Plant.id.

## Instalación

1. Clonar el repositorio:  
   git clone <url-del-repo>  
   cd agrodetect-backend

2. Crear un entorno virtual (recomendado):  
   python -m venv venv  
   source venv/bin/activate  (En Windows: venv\Scripts\activate)

3. Instalar dependencias:  
   pip install flask flask-cors python-dotenv requests

## Configuración

El sistema requiere variables de entorno para funcionar. Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:  

PLANT_ID_API_KEY=tu_api_key_aqui  

Sin esta clave, el servicio PlantBioEngine lanzará un error crítico al iniciar.

## Ejecución

Para levantar el servidor en modo desarrollo:  
python app.py  

- Host: 0.0.0.0 (Accesible desde red externa)  
- Puerto: 5000  
- Logs: Salida estándar (stdout)

## Documentación de la API

### 1. Health Check

Verifica que el servicio está operativo.  

Endpoint: GET /health  

Respuesta:  
{  
  "status": "online",  
  "service": "AgroDetect API v2 (Demo)"  
}

### 2. Analizar Planta

Realiza el análisis completo de espectro (taxonomía + salud).  

Endpoint: POST /agrosync-api/analyze  
Headers: Content-Type: application/json  
Límite de Payload: 16 MB

Cuerpo de la Petición (Opción A - URL):  
{  
  "image_url": "https://ejemplo.com/foto_hoja.jpg"  
}

Cuerpo de la Petición (Opción B - Base64):  
{  
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."  
}

Respuesta Exitosa (200 OK):  
{  
  "meta": {  
    "scan_date": "2023-10-27T10:00:00",  
    "is_plant_probability": 0.98,  
    "geo_mode": "global_demo"  
  },  
  "taxonomy": {  
    "scientific_name": "Monstera deliciosa",  
    "probability": 0.95,  
    "common_names": ["Costilla de Adán"],  
    "description": "Planta trepadora endémica de...",  
    "image_refs": ["url1", "url2"]  
  },  
  "health_assessment": {  
    "is_healthy": false,  
    "healthy_probability": 0.45,  
    "diseases": [  
      {  
        "name": "Leaf spot",  
        "probability": 0.88,  
        "treatments": {  
          "chemical": ["Fungicida X"],  
          "biological": ["Aceite de Neem"],  
          "prevention": ["Evitar exceso de riego"]  
        }  
      }  
    ]  
  }  
}

## Estructura del Proyecto

- app.py: Controlador principal. Gestiona el servidor HTTP, validación de inputs (JSON, Base64/URL), manejo de errores y logging.  
- plantbioengine.py: Capa de Lógica de Negocio. Encapsula la comunicación con la API externa, parsea los resultados complejos y formatea la salida simplificada para el cliente agrosync.

## Notas de Desarrollo

- Geolocalización: El código tiene preparada la lógica para recibir lat y lon en plantbioengine.py, pero actualmente se fuerza a None para permitir demostraciones con imágenes genéricas de internet sin sesgar al modelo por bioma. Para pasar a producción, descomentar las líneas correspondientes en app.py.  
- Manejo de Errores: Se implementa un manejo robusto de excepciones. Errores de API externa devuelven 502 Bad Gateway, errores de input 400/415, y errores internos 500.
