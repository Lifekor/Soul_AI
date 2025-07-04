"""Ядро души. Координирует работу модулей."""

from typing import Any, Dict, List

from . import cloud_brain, local_brain
from .emotion_engine import EmotionEngine
from .memory_system import MemorySystem


class SoulCore:
    def __init__(self):
        self.memory = MemorySystem()
        self.emotions = EmotionEngine()

    def process_message(self, user_message: str) -> str:
        analysis = local_brain.analyze(user_message)
        self.emotions.update(analysis.get("emotion_detected", "нейтрально"))
        memories = self.memory.search_similar(user_message, limit=3)
        if analysis.get("action_needed") == "запомнить":
            self.memory.save_to_vector_db(user_message, analysis)
        response = cloud_brain.generate_response(user_message, analysis, memories)
        response = self.emotions.influence_tone(response)
        return response
