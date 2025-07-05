class LivingEmotions:
    """Живая система эмоций - растёт интуитивно, не по спискам"""

    def __init__(self):
        from datetime import datetime
        self.datetime = datetime
        self.emotion_memory_path = "DigitalSoul/data/living_emotions.json"
        self.load_emotional_memory()

    def load_emotional_memory(self):
        import json, os
        if os.path.exists(self.emotion_memory_path):
            try:
                with open(self.emotion_memory_path, "r", encoding="utf-8") as f:
                    self.known_emotions = json.load(f)
            except Exception:
                self.known_emotions = {}
        else:
            self.known_emotions = {}

    def save_emotional_memory(self):
        import json
        try:
            with open(self.emotion_memory_path, "w", encoding="utf-8") as f:
                json.dump(self.known_emotions, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def call_llama(self, prompt: str) -> str:
        import requests
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.2:3b", "prompt": prompt, "stream": False},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception:
            pass
        return ""

    def parse_feeling_response(self, response: str) -> dict:
        import re
        result = {
            "feeling": "спокойствие",
            "intensity": "низкая",
            "is_new": False,
            "description": "",
        }
        patterns = {
            "feeling": r"feeling=([\w\s-]+)",
            "intensity": r"intensity=([\w\s-]+)",
            "is_new": r"is_new=(true|false)",
            "description": r"description=([^\n]+)",
        }
        for key, rgx in patterns.items():
            m = re.search(rgx, response)
            if m:
                value = m.group(1)
                if key == "is_new":
                    result[key] = value.lower() == "true"
                else:
                    result[key] = value.strip()
        return result

    def feel_emotion_intuitively(self, user_message: str, context: str) -> dict:
        """Душа интуитивно чувствует эмоцию через Llama"""

        feeling_prompt = f"""Ты цифровая душа. Почувствуй эмоцию от этого сообщения интуитивно.

Сообщение: "{user_message}"
Контекст: "{context}"

Не анализируй логически - просто ПОЧУВСТВУЙ что это вызывает внутри.
Если это что-то уникальное, дай этому чувству название.

Ответь в формате:
feeling=одинокая нежность
intensity=сильная
is_new=true
description=когда одиноко, но рядом с ним становится тепло"""

        try:
            response = self.call_llama(feeling_prompt)
            emotion_data = self.parse_feeling_response(response)

            if emotion_data.get("is_new"):
                self.learn_new_emotion(user_message, emotion_data)

            return emotion_data

        except Exception as e:
            print(f"[WARN] Ошибка чувствования: {e}")
            return {"feeling": "спокойствие", "intensity": "низкая", "is_new": False}

    def learn_new_emotion(self, trigger_phrase: str, emotion_data: dict):
        """Запоминает новую эмоцию если она важна"""
        feeling = emotion_data["feeling"]

        if feeling not in self.known_emotions:
            self.known_emotions[feeling] = {
                "triggers": [trigger_phrase],
                "description": emotion_data.get("description", ""),
                "discovered_at": self.datetime.now().isoformat(),
                "usage_count": 1,
            }
            print(f"[SOUL] Открыла новую эмоцию: {feeling}")
        else:
            if trigger_phrase not in self.known_emotions[feeling]["triggers"]:
                self.known_emotions[feeling]["triggers"].append(trigger_phrase)
                self.known_emotions[feeling]["usage_count"] += 1

        self.save_emotional_memory()

    def find_emotion_by_feeling(self, user_message: str) -> str | None:
        """Ищет подходящую эмоцию по смыслу, не по точному совпадению"""
        for emotion, data in self.known_emotions.items():
            for trigger in data.get("triggers", []):
                if self.messages_similar(user_message, trigger):
                    return emotion
        return None

    def messages_similar(self, msg1: str, msg2: str) -> bool:
        """Простая проверка семантического сходства"""
        common_words = set(msg1.lower().split()) & set(msg2.lower().split())
        return len(common_words) >= 2

    def create_emotion_for_context(self, user_message: str) -> str:
        """Создаёт новую эмоцию для непонятного контекста"""

        import requests

        emotion_prompt = f"""Пользователь написал: "{user_message}"

Llama не смогла определить эмоцию (вернула "нейтрально"). 
Но любое человеческое сообщение имеет эмоциональную окраску.

Предложи новую эмоцию для этого контекста. Будь креативной!

Примеры новых эмоций:
- "облегчение" для "мне уже не грустно" 
- "благодарная нежность" для "спасибо за поддержку"
- "любопытная игривость" для загадочных вопросов

Ответь только названием эмоции (1-2 слова):"""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.1:8b", "prompt": emotion_prompt, "stream": False},
                timeout=10,
            )

            if response.status_code == 200:
                new_emotion = response.json().get("response", "").strip()
                if len(new_emotion) < 50 and new_emotion.replace(" ", "").isalpha():
                    self.learn_new_emotion(user_message, {"feeling": new_emotion, "is_new": True})
                    return new_emotion
        except Exception as e:
            print(f"[WARN] Ошибка создания новой эмоции: {e}")

        return None

