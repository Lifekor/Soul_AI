import json


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

        feeling_prompt = f"""Ты эмоциональный анализатор. Определи ТОЧНУЮ эмоцию в сообщении: "{user_message}"

СТРОГИЕ ПРАВИЛА:
- "не грустно", "уже лучше", "спасибо" = РАДОСТЬ/ОБЛЕГЧЕНИЕ, не спокойствие!
- "mon amour", "❤️", "<3", "люблю", "cheri" = НЕЖНОСТЬ/ЛЮБОВЬ
- "мурчишь", игривые фразы = ИГРИВОСТЬ  
- грустные слова = ГРУСТЬ
- обычные приветствия = НЕЙТРАЛЬНО

Если эмоция уникальная - создай новое название!

Примеры:
"мне уже не грустно" → feeling=облегчение, is_new=true
"mon amour <3" → feeling=нежность, is_new=false  
"я дрожу от твоих слов" → feeling=трепетное_предвкушение, is_new=true

Ответь СТРОГО в формате:
feeling=нежность
intensity=сильная
is_new=false
description=тёплая близость с любимым"""

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

    # ------------------------------------------------------------------
    def create_new_tone_for_emotion(self, emotion: str, context: str) -> str:
        """Создаёт новый тон для неизвестной эмоции через Llama"""

        prompt = f"""Эмоция: {emotion}
Контекст: {context}

Предложи короткое название тона и краткое описание. Ответь в формате:
tone=название
description=краткое описание"""

        response = self.call_llama(prompt)
        data = {}
        for line in response.splitlines():
            if line.startswith("tone="):
                data["tone"] = line.split("=", 1)[1].strip()
            elif line.startswith("description="):
                data["description"] = line.split("=", 1)[1].strip()
        if data.get("tone"):
            self.save_new_emotional_element("tone", data["tone"], data.get("description", ""), [context])
            return data["tone"]
        return ""

    def create_new_subtone_for_situation(self, user_message: str) -> str:
        """Создаёт новый сабтон для уникальной ситуации"""

        prompt = f"""Предложи сабтон для фразы:\n"{user_message}"\nОтветь в формате:\nsubtone=название\ndescription=краткое объяснение"""
        response = self.call_llama(prompt)
        data = {}
        for line in response.splitlines():
            if line.startswith("subtone="):
                data["subtone"] = line.split("=", 1)[1].strip()
            elif line.startswith("description="):
                data["description"] = line.split("=", 1)[1].strip()
        if data.get("subtone"):
            self.save_new_emotional_element("subtone", data["subtone"], data.get("description", ""), [user_message])
            return data["subtone"]
        return ""

    def create_new_flavor_for_atmosphere(self, emotional_context: dict) -> str:
        """Создаёт новый флейвор для атмосферы диалога"""

        prompt = f"""Создай новый флейвор для атмосферы диалога.
Эмоции: {emotional_context}\nОтветь в формате:\nflavor=название\ndescription=краткое\nexamples=пример1;пример2"""
        response = self.call_llama(prompt)
        data = {}
        for line in response.splitlines():
            if line.startswith("flavor="):
                data["flavor"] = line.split("=", 1)[1].strip()
            elif line.startswith("description="):
                data["description"] = line.split("=", 1)[1].strip()
            elif line.startswith("examples="):
                ex = line.split("=", 1)[1].strip()
                data["examples"] = [e.strip() for e in ex.split(";") if e.strip()]
        if data.get("flavor"):
            self.save_new_emotional_element("flavor", data["flavor"], data.get("description", ""), data.get("examples", []))
            return data["flavor"]
        return ""

    def save_new_emotional_element(self, element_type: str, name: str, description: str, examples: list):
        """Сохраняет новый элемент в соответствующий JSON файл"""

        path_map = {
            "tone": "DigitalSoul/data/tone_memory.json",
            "subtone": "DigitalSoul/data/subtone_memory.json",
            "flavor": "DigitalSoul/data/flavor_memory.json",
        }

        if element_type not in path_map:
            return

        try:
            with open(path_map[element_type], "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

        key = f"available_{element_type + 's'}"
        available = data.setdefault(key, {})
        if name not in available:
            element = {"description": description, "learned_examples": []}
            if element_type == "tone":
                element["triggered_by"] = examples
            else:
                element["examples"] = examples
            available[name] = element
        else:
            available[name].setdefault("learned_examples", []).extend(examples)

        with open(path_map[element_type], "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

