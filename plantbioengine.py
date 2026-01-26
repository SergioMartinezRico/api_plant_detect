import os
import json
import base64
import requests
from typing import Dict, Any, Optional

class PlantBioEngine:
    def __init__(self):
        self.api_key = os.environ.get("PLANT_ID_API_KEY")
        self.endpoint = "https://api.plant.id/v3/identification"
        
        if not self.api_key:
            raise ValueError("CRITICAL: La variable de entorno 'PLANT_ID_API_KEY' no está definida.")

    # Mantenemos los argumentos en la firma para futura compatibilidad
    def analyze_full_spectrum(self, image_bytes: bytes, lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
        try:
            base64_img = base64.b64encode(image_bytes).decode("utf-8")
            
            headers = {
                "Content-Type": "application/json",
                "Api-Key": self.api_key
            }
            
            data = {
                "images": [base64_img],
                "health": "all",          
                "similar_images": True,   
                "classification_level": "species"
            }

            # [NOTE] ARQUITECTURA GEOGRÁFICA (Desactivada para Demo)
            # La geolocalización aumenta la precisión filtrando especies por bioma.
            # Se deja comentada para permitir pruebas genéricas (fotos de internet/interiores) sin sesgar al modelo.
            # -------------------------------------------------------
            # if lat is not None and lon is not None:
            #     data["latitude"] = lat
            #     data["longitude"] = lon
            # -------------------------------------------------------

            response = requests.post(self.endpoint, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            api_response = response.json()

            if not api_response or 'result' not in api_response:
                return {"error": "La API de Plant.id devolvió una respuesta vacía o malformada."}

            result = api_response['result']
            
            full_data = {
                "meta": {
                    "scan_date": result.get('created'),
                    "is_plant_probability": result.get('is_plant', {}).get('probability', 0),
                    "geo_mode": "global_demo" # Flag para saber que fue sin coordenadas
                },
                "taxonomy": {},
                "health_assessment": {
                    "is_healthy": False,
                    "diseases": []
                }
            }

            # A. Parsing Taxonómico
            classification = result.get('classification', {}).get('suggestions', [])
            if classification:
                top_match = classification[0]
                details = top_match.get('details', {})
                
                full_data["taxonomy"] = {
                    "scientific_name": top_match['name'],
                    "probability": top_match['probability'],
                    "common_names": details.get('common_names', []),
                    "description": details.get('description', {}).get('value', "Sin descripción disponible."),
                    "wiki_url": details.get('url'),
                    "taxonomy_tree": details.get('taxonomy', {}), 
                    "image_refs": [img['url'] for img in top_match.get('similar_images', [])][:2]
                }

            # B. Parsing de Salud
            is_healthy_prob = result.get('is_healthy', {}).get('probability', 0)
            full_data["health_assessment"]["healthy_probability"] = is_healthy_prob
            full_data["health_assessment"]["is_healthy"] = is_healthy_prob > 0.85 

            # C. Parsing de Patologías
            diseases_raw = result.get('disease', {}).get('suggestions', [])
            
            for d in diseases_raw:
                if d['probability'] > 0.15: 
                    d_details = d.get('details', {})
                    treatment = d_details.get('treatment', {})
                    
                    disease_entry = {
                        "name": d['name'],
                        "common_names": d_details.get('common_names', []),
                        "probability": d['probability'],
                        "description": d_details.get('description', ""),
                        "treatments": {
                            "chemical": treatment.get('chemical', []),
                            "biological": treatment.get('biological', []),
                            "prevention": treatment.get('prevention', [])
                        },
                        "classification": d_details.get('classification', [])
                    }
                    full_data["health_assessment"]["diseases"].append(disease_entry)

            return full_data

        except requests.exceptions.Timeout:
            return {"error": "Timeout: La API de Plant.id tardó demasiado en responder."}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error de conexión con Plant.id: {str(e)}"}
        except Exception as e:
            return {"error": f"Error interno en Engine: {str(e)}"}