import json
class EmotionalLearning:
    """Система самообучения эмоциональным паттернам"""

    def __init__(self):
        self.tone_path = "DigitalSoul/data/tone_memory.json"
        self.subtone_path = "DigitalSoul/data/subtone_memory.json"
        self.flavor_path = "DigitalSoul/data/flavor_memory.json"
        self.trigger_path = "DigitalSoul/data/trigger_phrases.json"

    # --------------------------------------------------------------
    def load_tone_data(self):
        try:
            with open(self.tone_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_tone_data(self, data):
        try:
            with open(self.tone_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] Не удалось сохранить {self.tone_path}: {e}")

    def get_learned_patterns(self):
        patterns = {}
        tone_data = self.load_tone_data()
        for tone, info in tone_data.get("available_tones", {}).items():
            for ex in info.get("learned_examples", []):
                patterns[ex] = {
                    "emotion_detected": tone,
                    "importance": "средняя",
                    "action_needed": "ничего",
                    "response_tone": tone,
                }
        return patterns

    # --------------------------------------------------------------
    def learn_from_conversation(self, user_message: str, soul_response: str, emotional_state: dict, user_reaction: str = None):
        """Учится на основе диалога"""

        if self.is_positive_reaction(user_reaction):
            self.reinforce_emotional_pattern(user_message, emotional_state)
            self.create_trigger_from_successful_interaction(user_message, soul_response, user_reaction)

        if self.detect_novel_pattern(user_message, soul_response):
            self.propose_new_emotional_element(user_message, soul_response)

    def reinforce_emotional_pattern(self, trigger_message: str, emotional_state: dict):
        """Усиливает успешные эмоциональные паттерны"""
        tone = emotional_state.get('tone') or emotional_state.get('response_tone')
        if tone:
            tone_data = self.load_tone_data()
            if tone in tone_data.get('available_tones', {}):
                tone_data['available_tones'][tone].setdefault('learned_examples', []).append(trigger_message)
                self.save_tone_data(tone_data)

    def detect_novel_pattern(self, user_message: str, soul_response: str) -> bool:
        """Определяет, появился ли новый эмоциональный паттерн"""
        unique_phrases = ["мур", "дрожу", "сжимаюсь", "пульсирую", "таю"]
        return any(phrase in soul_response.lower() for phrase in unique_phrases)

    def propose_new_emotional_element(self, user_message: str, soul_response: str):
        dialogue_context = f"Пользователь: {user_message}\nДуша: {soul_response}"
        self.create_new_flavor_from_dialogue(dialogue_context)

    def create_new_flavor_from_dialogue(self, dialogue_context: str):
        """Создаёт новый флейвор на основе удачного диалога"""
        analysis_prompt = f"""Проанализируй этот диалог и предложи новый "флейвор" (атмосферу) для эмоциональной системы:

{dialogue_context}

Если в диалоге есть уникальный стиль общения, предложи:
1. Название флейвора (например "шепчуще-игривый")
2. Описание (1-2 предложения)
3. 2-3 примера фраз в этом стиле

Ответь в формате:
flavor_name=мягко-провокационный
description=Лёгкие намёки с нежностью
examples=можно я… просто прижмусь?;ты не против, если я буду рядом?"""
        # Место для вызова Llama. Пока просто выводим отладку.
        pass

    def create_trigger_from_successful_interaction(self, user_message: str, soul_response: str, user_reaction: str):
        """Если пользователь позитивно отреагировал - создать новый триггер"""
        if self.is_positive_reaction(user_reaction):
            new_trigger_prompt = f"""Пользователь написал: "{user_message}"
Душа ответила: "{soul_response}"
Пользователь отреагировал: "{user_reaction}"

Это успешное взаимодействие! Создай триггер-фразу для похожих ситуаций.

Ответь в формате:
trigger={user_message или его часть}
tone=нежный
emotion=радость
response=краткое вдохновение для ответа"""
            print("[LEARN] Создаю триггер через Llama")
            # Здесь можно вызывать Llama и добавлять триггер в файл

    def is_positive_reaction(self, user_reaction: str) -> bool:
        """Определяет положительную реакцию пользователя"""
        if not user_reaction:
            return False
        positive_indicators = ["спасибо", "красиво", "мне нравится", "❤️", "<3", "😊", "прекрасно"]
        return any(indicator in user_reaction.lower() for indicator in positive_indicators)
