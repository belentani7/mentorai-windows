import json
import re
import os
import difflib

class AssistantEngine:
    def __init__(self, knowledge_base_path):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        self.sensitive_patterns = [
            r'[a-zA-Z0-9]{32,}', # Posibles claves API o hashes
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', # Correos electrónicos
            r'\b(?:\d{4}-){3}\d{4}\b', # Tarjetas de crédito
            r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b', # Direcciones Bitcoin
            r'\b[xX][a-fA-F0-9]{40}\b', # Direcciones Ethereum/EVM
        ]

    def _load_knowledge_base(self):
        kb = {}
        if not os.path.exists(self.knowledge_base_path):
            print(f"Error: La ruta de la base de conocimiento no existe: {self.knowledge_base_path}")
            return kb

        for filename in os.listdir(self.knowledge_base_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.knowledge_base_path, filename)
                try:
                    if os.path.getsize(file_path) > 0:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            kb.update(data)
                except json.JSONDecodeError as e:
                    print(f"Error al decodificar JSON en {filename}: {e}")
                except Exception as e:
                    print(f"Error inesperado al cargar {filename}: {e}")
        return kb

    def _filter_sensitive_data(self, text):
        filtered_text = text
        for pattern in self.sensitive_patterns:
            filtered_text = re.sub(pattern, '[CONFIDENCIAL]', filtered_text)
        return filtered_text

    def _find_best_match(self, query):
        query_lower = query.lower()
        keys = list(self.knowledge_base.keys())
        
        # Búsqueda exacta primero
        for key in keys:
            if key.lower() in query_lower:
                return key
        
        # Búsqueda difusa (fuzzy matching)
        matches = difflib.get_close_matches(query_lower, [k.lower() for k in keys], n=1, cutoff=0.6)
        if matches:
            # Encontrar la clave original que coincide con el match en minúsculas
            for key in keys:
                if key.lower() == matches[0]:
                    return key
        
        return None

    def process_query(self, extracted_text):
        if not extracted_text:
            return {"status": "error", "message": "No se proporcionó texto para procesar."}

        clean_text = self._filter_sensitive_data(extracted_text.strip())
        match_key = self._find_best_match(clean_text)
        
        response = {
            "status": "success",
            "original_query": clean_text,
            "explanation": "Lo siento, no tengo información específica sobre esto todavía. Prueba con términos como 'cd', 'powershell', 'binance' o 'adb'.",
            "steps": [],
            "security_tips": []
        }

        if match_key:
            data = self.knowledge_base[match_key]
            response["explanation"] = data.get("explanation", "")
            response["steps"] = data.get("steps", [])
            response["security_tips"] = data.get("security_tips", [])
            response["matched_term"] = match_key
        
        return response

if __name__ == "__main__":
    # Prueba rápida del motor mejorado
    engine = AssistantEngine('/home/ubuntu/asistente_educativo/knowledge_base')
    print(engine.process_query("¿Cómo funciona binance?"))
    print(engine.process_query("mi email es juan@gmail.com y mi btc es 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"))
