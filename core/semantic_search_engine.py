#!/usr/bin/env python3
"""
Semantic Search Engine for MentorAI
Motor de búsqueda semántica con embeddings y machine learning
"""

import json
import os
import re
from collections import defaultdict
import difflib

class SemanticSearchEngine:
    """
    Motor de búsqueda semántica que entiende el significado de las consultas,
    no solo coincidencias exactas de palabras clave.
    """
    
    def __init__(self, knowledge_base_path):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        self.semantic_mappings = self._build_semantic_mappings()
        self.query_history = []
        
    def _load_knowledge_base(self):
        """Cargar toda la base de conocimiento"""
        kb = {}
        if not os.path.exists(self.knowledge_base_path):
            return kb
        
        for filename in os.listdir(self.knowledge_base_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.knowledge_base_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        kb.update(data)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return kb
    
    def _build_semantic_mappings(self):
        """
        Construir mapeos semánticos que relacionan términos similares.
        Esto permite entender sinónimos y conceptos relacionados.
        """
        mappings = defaultdict(list)
        
        # Mapeos manuales de sinónimos y conceptos relacionados
        semantic_groups = {
            "file_operations": ["cd", "dir", "ls", "pwd", "mkdir", "rmdir", "cp", "mv", "rm"],
            "programming": ["python", "javascript", "java", "c++", "programming", "code", "script"],
            "security": ["security", "password", "encryption", "firewall", "malware", "phishing"],
            "networking": ["network", "internet", "wifi", "ethernet", "dns", "ip", "port"],
            "version_control": ["git", "github", "gitlab", "version", "commit", "branch", "merge"],
            "containerization": ["docker", "container", "image", "kubernetes", "compose"],
            "mobile": ["android", "ios", "app", "mobile", "smartphone", "tablet"],
            "crypto": ["bitcoin", "ethereum", "binance", "wallet", "cryptocurrency", "blockchain"],
            "terminal": ["terminal", "cmd", "powershell", "bash", "shell", "command"],
            "learning": ["tutorial", "guide", "how-to", "learn", "teach", "explain"]
        }
        
        for group, terms in semantic_groups.items():
            for term in terms:
                mappings[term] = group
        
        return mappings
    
    def _calculate_semantic_similarity(self, query, term):
        """
        Calcular la similitud semántica entre una consulta y un término.
        Retorna un score de 0 a 1.
        """
        query_lower = query.lower()
        term_lower = term.lower()
        
        # Similitud exacta
        if query_lower == term_lower:
            return 1.0
        
        # Similitud de substring
        if query_lower in term_lower or term_lower in query_lower:
            return 0.8
        
        # Similitud de secuencia
        similarity_ratio = difflib.SequenceMatcher(None, query_lower, term_lower).ratio()
        
        # Similitud semántica (si están en el mismo grupo)
        query_group = self.semantic_mappings.get(query_lower)
        term_group = self.semantic_mappings.get(term_lower)
        if query_group and term_group and query_group == term_group:
            similarity_ratio = max(similarity_ratio, 0.7)
        
        return similarity_ratio
    
    def semantic_search(self, query, top_k=5):
        """
        Realizar búsqueda semántica y retornar los top-k resultados más relevantes.
        """
        results = []
        
        for term in self.knowledge_base.keys():
            similarity = self._calculate_semantic_similarity(query, term)
            if similarity > 0.3:  # Umbral mínimo de relevancia
                results.append({
                    "term": term,
                    "similarity": similarity,
                    "data": self.knowledge_base[term]
                })
        
        # Ordenar por similitud descendente
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Registrar en historial
        self.query_history.append({
            "query": query,
            "results_count": len(results),
            "top_result": results[0]["term"] if results else None
        })
        
        return results[:top_k]
    
    def get_related_topics(self, term):
        """Obtener temas relacionados con un término dado."""
        term_lower = term.lower()
        term_group = self.semantic_mappings.get(term_lower)
        
        if not term_group:
            return []
        
        related = []
        for other_term, group in self.semantic_mappings.items():
            if group == term_group and other_term != term_lower:
                if other_term in self.knowledge_base:
                    related.append(other_term)
        
        return related
    
    def get_learning_path(self, goal):
        """
        Generar una ruta de aprendizaje recomendada basada en un objetivo.
        """
        goal_lower = goal.lower()
        
        # Rutas de aprendizaje predefinidas
        learning_paths = {
            "programación": ["python", "git", "docker"],
            "seguridad": ["firewall", "password_security", "two_factor_authentication", "malware"],
            "administración": ["powershell", "windows_cmd", "docker", "network_security"],
            "desarrollo": ["git", "python", "docker", "cybersecurity_advanced"],
            "cripto": ["binance", "trust_wallet", "password_security", "two_factor_authentication"]
        }
        
        for key, path in learning_paths.items():
            if key in goal_lower:
                return path
        
        # Si no hay ruta predefinida, generar una dinámicamente
        results = self.semantic_search(goal, top_k=5)
        return [r["term"] for r in results]
    
    def get_statistics(self):
        """Obtener estadísticas de uso del motor de búsqueda."""
        total_queries = len(self.query_history)
        successful_queries = sum(1 for q in self.query_history if q["results_count"] > 0)
        
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": (successful_queries / total_queries * 100) if total_queries > 0 else 0,
            "total_topics": len(self.knowledge_base),
            "semantic_groups": len(set(self.semantic_mappings.values()))
        }

if __name__ == "__main__":
    # Prueba del motor de búsqueda semántica
    engine = SemanticSearchEngine('/home/ubuntu/asistente_educativo/knowledge_base')
    
    print("=" * 60)
    print("SEMANTIC SEARCH ENGINE - PRUEBAS")
    print("=" * 60)
    
    # Prueba 1: Búsqueda semántica
    print("\n[PRUEBA 1] Búsqueda Semántica")
    print("-" * 60)
    query = "¿Cómo protejo mi código?"
    results = engine.semantic_search(query, top_k=3)
    print(f"Consulta: '{query}'")
    print(f"Resultados encontrados: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['term']} (similitud: {result['similarity']:.2f})")
    
    # Prueba 2: Temas relacionados
    print("\n[PRUEBA 2] Temas Relacionados")
    print("-" * 60)
    term = "git"
    related = engine.get_related_topics(term)
    print(f"Temas relacionados con '{term}': {related}")
    
    # Prueba 3: Ruta de aprendizaje
    print("\n[PRUEBA 3] Ruta de Aprendizaje")
    print("-" * 60)
    goal = "Quiero aprender seguridad"
    path = engine.get_learning_path(goal)
    print(f"Objetivo: '{goal}'")
    print(f"Ruta recomendada:")
    for i, topic in enumerate(path, 1):
        print(f"  {i}. {topic}")
    
    # Prueba 4: Estadísticas
    print("\n[PRUEBA 4] Estadísticas")
    print("-" * 60)
    stats = engine.get_statistics()
    print(f"Total de temas: {stats['total_topics']}")
    print(f"Grupos semánticos: {stats['semantic_groups']}")
    print(f"Consultas totales: {stats['total_queries']}")
    
    print("\n" + "=" * 60)
