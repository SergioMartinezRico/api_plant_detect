import os
import base64
import logging
import sys
import requests 

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from plantbioengine import PlantBioEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
CORS(app, resources={r"/*": {"origins": "*"}})

try:
    engine = PlantBioEngine()
    logger.info("✅ Motor PlantBioEngine inicializado correctamente.")
except Exception as e:
    logger.critical(f"❌ Error crítico iniciando el motor: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "service": "AgroDetect API v2 (Demo)"}), 200

@app.route('/agrosync-api/analyze', methods=['POST'])
def analyze_plant():
    try:
        if not request.is_json:
            return jsonify({"error": "El cuerpo debe ser JSON"}), 415
            
        data = request.get_json()
        image_bytes = None

        if 'image_url' in data:
            image_url = data['image_url']
            logger.info(f"📥 Descargando imagen desde URL: {image_url}")
            try:
                img_response = requests.get(image_url, timeout=10)
                img_response.raise_for_status()
                image_bytes = img_response.content
            except Exception as e:
                return jsonify({"error": f"No se pudo descargar la imagen de la URL: {str(e)}"}), 400

        elif 'image_base64' in data:
            img_str = data['image_base64']
            if "," in img_str:
                img_str = img_str.split(",")[1]
            try:
                image_bytes = base64.b64decode(img_str)
            except Exception:
                return jsonify({"error": "Base64 inválido"}), 400
        else:
            return jsonify({"error": "Falta 'image_url' o 'image_base64'"}), 400

        # [TODO: PROD] Recuperar coordenadas reales del dron
        # lat = data.get('lat')
        # lon = data.get('lon')
        # Por ahora forzamos None para búsqueda global
        lat = None
        lon = None

        logger.info(f"Procesando imagen (Modo Demo)... (Tamaño: {len(image_bytes)} bytes)")
        
        # Llamamos pasando None explícitamente para documentar la intención
        result = engine.analyze_full_spectrum(image_bytes, lat=lat, lon=lon)

        if "error" in result:
            logger.error(f"Error en motor: {result['error']}")
            return jsonify(result), 502 
            
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error no controlado: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)