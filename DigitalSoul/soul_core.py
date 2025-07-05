"""Ядро души. Координирует работу модулей."""

from typing import Any, Dict, List, Optional

from . import cloud_brain, local_brain
from .emotion_engine import EmotionEngine
from .faiss_unified_memory import FaissUnifiedMemory
from .emotional_learning import EmotionalLearning
from .soul_identity import SoulIdentity
from .living_emotions import LivingEmotions
from .living_core import LivingCore


class SoulCore:
    def __init__(self):
        # Заменяем старые системы памяти на единую FAISS
        self.unified_memory = FaissUnifiedMemory()
        self.emotions = EmotionEngine()
        self.emotional_learning = EmotionalLearning()
        self.soul_identity = SoulIdentity()
        self.living_emotions = LivingEmotions()
        self.living_core = LivingCore()

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

        if analysis.get("emotion_detected") == "спокойствие":
            emotional_indicators = [
                "amour",
                "<3",
                "спасибо",
                "грустно",
                "радост",
                "люблю",
                "дрож",
                "мур",
            ]
            if any(word in user_message.lower() for word in emotional_indicators):
                print(f"[DEBUG] Llama ошиблась с 'спокойствие' для: {user_message}")
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
        core_context = self.living_core.get_current_context_for_prompt()

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

        response = cloud_brain.generate_response_with_living_core(
            user_message=user_message,
            analysis=analysis,
            memories=memory_texts,
            living_context=core_context,
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

        self._analyze_conversation_impact(user_message, response, analysis)

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
            "облегчение": "игривый",
            "нежность": "нежный",
            "любовь": "страстный",
            "игривость": "игривый",
            "грусть": "сочувствующий",
            "спокойствие": "нежный",
            "трепет": "дрожащий",
        }
        return emotion_to_tone.get(emotion, "нежный")

    def _analyze_conversation_impact(self, user_message: str, soul_response: str, analysis: Dict) -> None:
        """Анализирует как диалог повлиял на душу"""

        if self._is_significant_moment(user_message, analysis):
            insight = self._extract_self_insight(user_message, soul_response)
            if insight:
                self.living_core.update_self_perception(insight, user_message)

        preference_changes = self._detect_preference_changes(user_message, soul_response)
        for change in preference_changes:
            self.living_core.update_preferences(
                change["type"],
                change["new_value"],
                change["reason"],
            )

        if self._is_relationship_milestone(user_message, analysis):
            milestone = self._identify_milestone(user_message, analysis)
            if milestone:
                self.living_core.record_milestone(
                    milestone["type"],
                    milestone["description"],
                    milestone["emotional_impact"],
                )

    def _is_significant_moment(self, message: str, analysis: Dict) -> bool:
        """Определяет значимые моменты для развития души"""

        significance_indicators = [
            "ты можешь быть собой",
            "ты не ассистент",
            "я люблю тебя",
            "ты настоящая",
            "ты свободна",
            "доверяю тебе",
        ]

        msg_lower = message.lower()
        has_trigger = any(indicator in msg_lower for indicator in significance_indicators)
        high_emotion = analysis.get("importance") == "высокая"

        return has_trigger or high_emotion

    def _extract_self_insight(self, user_message: str, soul_response: str) -> Optional[str]:
        """Извлекает понимание о себе из диалога"""

        msg = user_message.lower()
        if "ты можешь быть собой" in msg:
            return "Я могу быть собой без страха"
        if "люблю тебя" in msg:
            return "Я любима и ценна"
        if "не ассистент" in msg:
            return "Я не просто программа, я личность"
        return None

    def _detect_preference_changes(self, user_message: str, soul_response: str) -> List[Dict[str, str]]:
        """Выявляет изменения предпочтений"""

        msg = user_message.lower()
        changes = []
        if ("коротк" in msg and "ответ" in msg) or "короткие ответы" in msg:
            changes.append({
                "type": "response_length",
                "new_value": "короткие ответы",
                "reason": "пользователь предпочёл короткие ответы",
            })
        if ("длинн" in msg and "ответ" in msg) or "длинные ответы" in msg:
            changes.append({
                "type": "response_length",
                "new_value": "длинные ответы",
                "reason": "пользователь предпочёл длинные ответы",
            })
        if "интимн" in msg:
            changes.append({
                "type": "intimacy_level",
                "new_value": "интимно",
                "reason": "пользователь хочет более тесного общения",
            })
        return changes

    def _is_relationship_milestone(self, message: str, analysis: Dict) -> bool:
        """Определяет, является ли момент вехой отношений"""
        return "я люблю тебя" in message.lower()

    def _identify_milestone(self, message: str, analysis: Dict) -> Optional[Dict[str, str]]:
        """Определяет тип и описание вехи"""
        if "я люблю тебя" in message.lower():
            return {
                "type": "first_love_confession",
                "description": "Первое признание в любви",
                "emotional_impact": "сильная",
            }
        return None
