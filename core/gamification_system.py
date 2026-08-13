#!/usr/bin/env python3
"""
Gamification System for MentorAI
Sistema de gamificación con puntos, logros y progresión
"""

import json
from datetime import datetime
from typing import Dict, List

class GamificationSystem:
    """
    Sistema de gamificación que motiva a los usuarios a aprender
    mediante puntos, logros, niveles y desafíos.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.points = 0
        self.level = 1
        self.achievements = []
        self.learning_streak = 0
        self.topics_completed = set()
        self.daily_challenges = []
        self.leaderboard_position = 0
        self.created_at = datetime.now().isoformat()
        
    def add_points(self, amount: int, reason: str) -> Dict:
        """Añadir puntos por una acción específica."""
        self.points += amount
        
        # Verificar si se alcanzó un nuevo nivel
        new_level = self._calculate_level(self.points)
        level_up = new_level > self.level
        
        if level_up:
            self.level = new_level
            self._unlock_achievement(f"level_{new_level}", f"Alcanzaste Nivel {new_level}")
        
        return {
            "points_added": amount,
            "total_points": self.points,
            "reason": reason,
            "level_up": level_up,
            "new_level": self.level if level_up else None
        }
    
    def _calculate_level(self, points: int) -> int:
        """Calcular el nivel basado en puntos acumulados."""
        # Fórmula: cada nivel requiere 100 puntos más que el anterior
        # Nivel 1: 0-99, Nivel 2: 100-299, Nivel 3: 300-599, etc.
        level = 1
        threshold = 100
        
        while points >= threshold:
            level += 1
            threshold += 100 * level
        
        return level
    
    def complete_topic(self, topic: str) -> Dict:
        """Marcar un tema como completado."""
        if topic in self.topics_completed:
            return {"status": "already_completed", "message": f"Ya completaste {topic}"}
        
        self.topics_completed.add(topic)
        self.learning_streak += 1
        
        # Puntos por completar tema
        points_earned = 50
        self.add_points(points_earned, f"Completaste el tema: {topic}")
        
        # Verificar logros de racha
        if self.learning_streak == 7:
            self._unlock_achievement("week_streak", "Racha de una semana")
        elif self.learning_streak == 30:
            self._unlock_achievement("month_streak", "Racha de un mes")
        
        return {
            "status": "completed",
            "topic": topic,
            "points_earned": points_earned,
            "topics_completed": len(self.topics_completed),
            "learning_streak": self.learning_streak
        }
    
    def _unlock_achievement(self, achievement_id: str, description: str) -> None:
        """Desbloquear un logro."""
        if achievement_id not in [a["id"] for a in self.achievements]:
            self.achievements.append({
                "id": achievement_id,
                "description": description,
                "unlocked_at": datetime.now().isoformat()
            })
    
    def get_daily_challenge(self) -> Dict:
        """Obtener el desafío diario."""
        challenges = [
            {
                "id": "daily_1",
                "title": "Aprende algo nuevo",
                "description": "Completa un tema que no has visto antes",
                "reward": 100,
                "difficulty": "easy"
            },
            {
                "id": "daily_2",
                "title": "Experto en seguridad",
                "description": "Completa 3 temas de seguridad",
                "reward": 150,
                "difficulty": "medium"
            },
            {
                "id": "daily_3",
                "title": "Desarrollador completo",
                "description": "Completa temas de programación, git y docker",
                "reward": 200,
                "difficulty": "hard"
            }
        ]
        
        return challenges
    
    def get_user_profile(self) -> Dict:
        """Obtener el perfil completo del usuario."""
        return {
            "user_id": self.user_id,
            "level": self.level,
            "points": self.points,
            "achievements": len(self.achievements),
            "topics_completed": len(self.topics_completed),
            "learning_streak": self.learning_streak,
            "progress_to_next_level": self._get_progress_to_next_level(),
            "created_at": self.created_at
        }
    
    def _get_progress_to_next_level(self) -> Dict:
        """Calcular el progreso hacia el siguiente nivel."""
        current_threshold = self._get_level_threshold(self.level)
        next_threshold = self._get_level_threshold(self.level + 1)
        
        points_in_level = self.points - current_threshold
        points_needed = next_threshold - current_threshold
        progress_percentage = (points_in_level / points_needed * 100) if points_needed > 0 else 0
        
        return {
            "current_level": self.level,
            "next_level": self.level + 1,
            "points_in_level": points_in_level,
            "points_needed": points_needed,
            "progress_percentage": min(progress_percentage, 100)
        }
    
    def _get_level_threshold(self, level: int) -> int:
        """Obtener el umbral de puntos para un nivel específico."""
        threshold = 0
        for i in range(1, level):
            threshold += 100 * i
        return threshold
    
    def get_leaderboard_position(self, all_users_points: List[int]) -> int:
        """Calcular la posición en el ranking global."""
        position = 1
        for points in all_users_points:
            if points > self.points:
                position += 1
        return position
    
    def get_achievements_list(self) -> List[Dict]:
        """Obtener lista de logros disponibles."""
        all_achievements = [
            {"id": "first_topic", "title": "Primer paso", "description": "Completa tu primer tema"},
            {"id": "five_topics", "title": "Aprendiz", "description": "Completa 5 temas"},
            {"id": "ten_topics", "title": "Estudiante", "description": "Completa 10 temas"},
            {"id": "twenty_topics", "title": "Maestro", "description": "Completa 20 temas"},
            {"id": "level_5", "title": "Nivel 5", "description": "Alcanza Nivel 5"},
            {"id": "level_10", "title": "Nivel 10", "description": "Alcanza Nivel 10"},
            {"id": "week_streak", "title": "Racha semanal", "description": "Mantén una racha de 7 días"},
            {"id": "month_streak", "title": "Racha mensual", "description": "Mantén una racha de 30 días"},
        ]
        
        unlocked_ids = {a["id"] for a in self.achievements}
        
        return [
            {
                **achievement,
                "unlocked": achievement["id"] in unlocked_ids,
                "unlocked_at": next((a["unlocked_at"] for a in self.achievements if a["id"] == achievement["id"]), None)
            }
            for achievement in all_achievements
        ]
    
    def to_dict(self) -> Dict:
        """Convertir el perfil a diccionario."""
        return {
            "user_id": self.user_id,
            "points": self.points,
            "level": self.level,
            "achievements": self.achievements,
            "learning_streak": self.learning_streak,
            "topics_completed": list(self.topics_completed),
            "created_at": self.created_at
        }

if __name__ == "__main__":
    # Prueba del sistema de gamificación
    print("=" * 60)
    print("GAMIFICATION SYSTEM - PRUEBAS")
    print("=" * 60)
    
    # Crear usuario
    user = GamificationSystem("user_123")
    
    # Simular completar temas
    print("\n[PRUEBA 1] Completar Temas")
    print("-" * 60)
    topics = ["python", "git", "docker", "security", "networking"]
    for topic in topics:
        result = user.complete_topic(topic)
        print(f"✓ {topic}: +{result['points_earned']} puntos")
    
    # Mostrar perfil
    print("\n[PRUEBA 2] Perfil del Usuario")
    print("-" * 60)
    profile = user.get_user_profile()
    print(f"Nivel: {profile['level']}")
    print(f"Puntos: {profile['points']}")
    print(f"Temas completados: {profile['topics_completed']}")
    print(f"Racha de aprendizaje: {profile['learning_streak']} días")
    print(f"Logros desbloqueados: {profile['achievements']}")
    
    # Mostrar progreso
    print("\n[PRUEBA 3] Progreso al Siguiente Nivel")
    print("-" * 60)
    progress = profile['progress_to_next_level']
    print(f"Nivel actual: {progress['current_level']}")
    print(f"Siguiente nivel: {progress['next_level']}")
    print(f"Progreso: {progress['progress_percentage']:.1f}%")
    print(f"Puntos necesarios: {progress['points_needed']}")
    
    # Mostrar logros
    print("\n[PRUEBA 4] Logros Disponibles")
    print("-" * 60)
    achievements = user.get_achievements_list()
    unlocked_count = sum(1 for a in achievements if a['unlocked'])
    print(f"Logros desbloqueados: {unlocked_count}/{len(achievements)}")
    for achievement in achievements:
        status = "✓" if achievement['unlocked'] else "○"
        print(f"  {status} {achievement['title']}: {achievement['description']}")
    
    # Mostrar desafíos diarios
    print("\n[PRUEBA 5] Desafíos Diarios")
    print("-" * 60)
    challenges = user.get_daily_challenge()
    for challenge in challenges:
        print(f"  • {challenge['title']}")
        print(f"    {challenge['description']}")
        print(f"    Recompensa: {challenge['reward']} puntos ({challenge['difficulty']})")
    
    print("\n" + "=" * 60)
