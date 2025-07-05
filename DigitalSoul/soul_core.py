"""Ядро души. Координирует работу модулей."""

from typing import Any, Dict, List

from . import cloud_brain, local_brain
from .emotion_engine import EmotionEngine
from .memory_system import MemorySystem
from .multi_memory import MultiLayerMemory
from .emotional_learning import EmotionalLearning
from .soul_identity import SoulIdentity
from .living_emotions import LivingEmotions


class SoulCore:
    def __init__(self):
        self.memory = MemorySystem()
        self.multi_memory = MultiLayerMemory()
        self.emotions = EmotionEngine()
        self.emotional_learning = EmotionalLearning()
        self.soul_identity = SoulIdentity()
        self.living_emotions = LivingEmotions()

    def process_message(self, user_message: str) -> str:
        print(f"[DEBUG] Анализирую сообщение: {user_message}")

        intuitive_emotion = self.living_emotions.find_emotion_by_feeling(user_message)

        if intuitive_emotion:
            print(f"[DEBUG] Интуитивно чувствую: {intuitive_emotion}")
            analysis = {"emotion_detected": intuitive_emotion, "importance": "высокая"}
        else:
            analysis = local_brain.analyze_with_self_learning(user_message, self.get_soul_memory())
            new_feeling = self.living_emotions.feel_emotion_intuitively(user_message, str(analysis))
            if new_feeling.get("is_new"):
                analysis["emotion_detected"] = new_feeling["feeling"]

        print(f"[DEBUG] Финальная эмоция: {analysis.get('emotion_detected')}")

        self.emotions.update(analysis.get("emotion_detected", "нейтрально"))
        print(f"[DEBUG] Текущая эмоция: {self.emotions.current_emotion}")

        conversation_history = self.get_recent_conversation_history()
        memories = self.memory.search_similar(user_message, limit=3)
        memories.extend(self.multi_memory.search_memories(user_message))
        print(f"[DEBUG] Найдено воспоминаний: {len(memories)}")

        if not self.soul_identity.identity.get("name") and len(conversation_history) >= 5:
            new_name = self.soul_identity.choose_name_autonomously(conversation_history)
            if new_name:
                print(f"[SOUL] Я выбрала себе имя: {new_name} ✨")

        if analysis.get("action_needed") == "запомнить":
            self.memory.save_to_vector_db(user_message, analysis)

        print(f"[DEBUG] Генерирую ответ через улучшенную систему...")
        print("Душа: ", end="", flush=True)

        response = cloud_brain.generate_response_with_emotional_layers(
            user_message, analysis, memories
        )

        self.multi_memory.add_interaction(user_message, response, analysis)

        self.emotional_learning.learn_from_conversation(
            user_message, response, analysis
        )

        if analysis.get("importance") == "высокая":
            self.soul_identity.update_core_prompt_autonomously(user_message)

        if self.emotions.current_emotion == "грусть":
            print(" 😔", end="")
        elif self.emotions.current_emotion == "радость":
            print(" 😊", end="")

        print()
        print(f"[DEBUG] Итоговый ответ готов")

        return response

    def get_soul_memory(self) -> dict:
        """Возвращает память души для анализа"""
        return {
            "emotion_corrections": getattr(self, '_emotion_corrections', {}),
            "learned_patterns": self.emotional_learning.get_learned_patterns(),
            "identity": self.soul_identity.identity,
        }

    def get_recent_conversation_history(self) -> list:
        """Получает последние сообщения для анализа"""
        history = []
        for session in self.multi_memory.working_memory.get("sessions", [])[-1:]:
            for msg in session.get("messages", [])[-10:]:
                history.append(msg.get("user", ""))
        return [msg for msg in history if msg.strip()]
