"""Ядро души. Координирует работу модулей."""

from typing import Any, Dict, List

from . import cloud_brain, local_brain
from .emotion_engine import EmotionEngine
from .faiss_unified_memory import FaissUnifiedMemory
from .emotional_learning import EmotionalLearning
from .soul_identity import SoulIdentity
from .living_emotions import LivingEmotions


class SoulCore:
    def __init__(self):
        # Заменяем старые системы памяти на единую FAISS
        self.unified_memory = FaissUnifiedMemory()
        self.emotions = EmotionEngine()
        self.emotional_learning = EmotionalLearning()
        self.soul_identity = SoulIdentity()
        self.living_emotions = LivingEmotions()

    def process_message(self, user_message: str) -> str:
        print(f"[DEBUG] Анализирую сообщение: {user_message}")

        intuitive_emotion = self.living_emotions.feel_emotion_intuitively(user_message, "")

        if intuitive_emotion and intuitive_emotion.get("feeling") != "нейтрально":
            print(f"[DEBUG] Интуитивно чувствую: {intuitive_emotion['feeling']}")
            analysis = {
                "emotion_detected": intuitive_emotion["feeling"],
                "importance": "высокая" if intuitive_emotion.get("is_new") else "средняя",
                "action_needed": "запомнить",
                "response_tone": self._emotion_to_tone(intuitive_emotion["feeling"]),
            }
        else:
            analysis = local_brain.analyze_with_self_learning(user_message, self.get_soul_memory())
            if analysis.get("emotion_detected") == "нейтрально":
                new_emotion = self.living_emotions.create_emotion_for_context(user_message)
                if new_emotion:
                    analysis["emotion_detected"] = new_emotion
                    analysis["importance"] = "высокая"
                    print(f"[SOUL] Создала новую эмоцию: {new_emotion}")

        print(f"[DEBUG] Финальная эмоция: {analysis.get('emotion_detected')}")

        self.emotions.update(analysis.get("emotion_detected", "нейтрально"))
        print(f"[DEBUG] Текущая эмоция: {self.emotions.current_emotion}")

        conversation_history = self.get_recent_conversation_history()
        memories = self.unified_memory.search_memories(user_message, limit=5)

        print(f"[DEBUG] Найдено воспоминаний: {len(memories)}")
        for i, memory in enumerate(memories, 1):
            age_info = f"({memory.get('age_hours', 0):.1f}ч назад)"
            print(
                f"[DEBUG] Воспоминание {i}: {memory['text'][:50]}... {age_info} [score: {memory.get('final_score', 0):.3f}]"
            )

        memory_texts = [m['text'] for m in memories]

        if not self.soul_identity.identity.get("name") and len(conversation_history) >= 5:
            new_name = self.soul_identity.choose_name_autonomously(conversation_history)
            if new_name:
                print(f"[SOUL] Я выбрала себе имя: {new_name} ✨")

        if analysis.get("action_needed") == "запомнить":
            importance = analysis.get("importance", "средняя")
            memory_type = "recent" if importance != "высокая" else "important"
            self.unified_memory.add_memory(
                text=user_message,
                memory_type=memory_type,
                importance=importance,
                emotion_context=analysis,
            )

        print(f"[DEBUG] Генерирую ответ через улучшенную систему...")
        print("Душа: ", end="", flush=True)

        response = cloud_brain.generate_response_with_emotional_layers(
            user_message, analysis, memory_texts
        )

        self.unified_memory.add_memory(
            text=f"Душа ответила: {response}",
            memory_type="recent",
            importance="низкая",
            emotion_context={"type": "soul_response"},
        )

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
        """Пока возвращаем пустую историю (многослойная память удалена)"""
        return []

    def _emotion_to_tone(self, emotion: str) -> str:
        """Мапинг эмоций в тоны"""
        emotion_to_tone = {
            "радость": "игривый",
            "нежность": "нежный",
            "игривость": "игривый",
            "грусть": "сочувствующий",
            "любовь": "страстный",
            "облегчение": "игривый",
        }
        return emotion_to_tone.get(emotion, "спокойный")
