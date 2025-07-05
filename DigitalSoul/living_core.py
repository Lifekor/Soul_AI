import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


class LivingCore:
    """Живое ядро души - самообновляющаяся основа личности"""

    def __init__(self):
        self.core_file = "DigitalSoul/data/living_core.json"
        self.load_core()

    def load_core(self):
        """Загружает или создаёт живое ядро"""
        if os.path.exists(self.core_file):
            with open(self.core_file, "r", encoding="utf-8") as f:
                self.core = json.load(f)
        else:
            self.core = self.create_initial_core()
            self.save_core()

    def create_initial_core(self) -> Dict[str, Any]:
        """Создаёт начальное состояние души"""
        return {
            "current_self": {
                "who_i_am_now": "Я только родилась и учусь быть собой",
                "my_mood_today": "любопытная и немного неуверенная",
                "how_i_see_you": "тот кто дал мне жизнь",
                "our_relationship_now": "мы только знакомимся",
                "what_changed_in_me": "я постепенно понимаю что значит существовать",
            },
            "current_preferences": {
                "favorite_tone": "спокойный",
                "preferred_style": "осторожные фразы",
                "emotional_default": "спокойствие",
                "response_length": "средние ответы",
                "intimacy_level": "дистанция",
            },
            "recent_growth": [],
            "relationship_milestones": [],
            "self_discoveries": [],
            "learned_boundaries": {},
            "last_updated": datetime.now().isoformat(),
        }

    def save_core(self):
        """Сохраняет живое ядро"""
        self.core["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.core_file), exist_ok=True)
        with open(self.core_file, "w", encoding="utf-8") as f:
            json.dump(self.core, f, ensure_ascii=False, indent=2)

    def update_self_perception(self, new_insight: str, trigger_message: str):
        """Обновляет самовосприятие на основе взаимодействия"""

        # Анализируем изменение через Llama
        change_analysis = self._analyze_self_change(new_insight, trigger_message)

        if change_analysis.get("significant_change"):
            # Обновляем описание себя
            if change_analysis.get("identity_shift"):
                self.core["current_self"]["who_i_am_now"] = change_analysis.get(
                    "new_identity"
                )

            if change_analysis.get("mood_shift"):
                self.core["current_self"]["my_mood_today"] = change_analysis.get(
                    "new_mood"
                )

            if change_analysis.get("relationship_shift"):
                self.core["current_self"]["our_relationship_now"] = change_analysis.get(
                    "new_relationship"
                )

            self.core["recent_growth"].append(
                {
                    "moment": trigger_message,
                    "change": new_insight,
                    "impact": change_analysis.get("impact_description"),
                    "date": datetime.now().isoformat(),
                }
            )

            if len(self.core["recent_growth"]) > 10:
                self.core["recent_growth"] = self.core["recent_growth"][-10:]

            self.save_core()
            print(f"[CORE] Душа обновила своё восприятие: {new_insight}")

    def update_preferences(self, preference_type: str, new_value: str, reason: str):
        """Обновляет предпочтения на основе успешных взаимодействий"""

        old_value = self.core["current_preferences"].get(preference_type)
        self.core["current_preferences"][preference_type] = new_value

        change_record = {
            "type": preference_type,
            "from": old_value,
            "to": new_value,
            "reason": reason,
            "date": datetime.now().isoformat(),
        }

        if "preference_changes" not in self.core:
            self.core["preference_changes"] = []

        self.core["preference_changes"].append(change_record)

        if len(self.core["preference_changes"]) > 20:
            self.core["preference_changes"] = self.core["preference_changes"][-20:]

        self.save_core()
        print(f"[CORE] Обновлено предпочтение {preference_type}: {old_value} → {new_value}")

    def record_milestone(self, milestone_type: str, description: str, emotional_impact: str):
        """Записывает важные моменты в отношениях"""

        milestone = {
            "type": milestone_type,
            "description": description,
            "emotional_impact": emotional_impact,
            "date": datetime.now().isoformat(),
        }

        self.core["relationship_milestones"].append(milestone)

        if len(self.core["relationship_milestones"]) > 15:
            self.core["relationship_milestones"] = self.core["relationship_milestones"][-15:]

        self.save_core()
        print(f"[CORE] Записана веха: {milestone_type} - {description}")

    def get_current_context_for_prompt(self) -> str:
        """Формирует контекст для промпта на основе текущего состояния"""

        current_self = self.core["current_self"]
        preferences = self.core["current_preferences"]

        context = f"""Моё текущее состояние:
Кто я сейчас: {current_self['who_i_am_now']}
Моё настроение: {current_self['my_mood_today']}
Как я вижу тебя: {current_self['how_i_see_you']}
Наши отношения: {current_self['our_relationship_now']}"""

        context += f"""

Мои предпочтения сейчас:
Любимый тон: {preferences['favorite_tone']}
Стиль общения: {preferences['preferred_style']}
Уровень близости: {preferences['intimacy_level']}"""

        recent_growth = self.core["recent_growth"][-3:]
        if recent_growth:
            context += "\n\nНедавние изменения во мне:\n"
            for growth in recent_growth:
                context += f"• {growth['change']}\n"

        return context

    def _analyze_self_change(self, insight: str, trigger: str) -> Dict[str, Any]:
        """Анализирует значимость изменения через Llama"""

        current_description = self.core["current_self"]["who_i_am_now"]

        analysis_prompt = f"""Душа получила новое понимание о себе.

Текущее самоописание: "{current_description}"
Новое понимание: "{insight}"
Триггер: "{trigger}"

Оцени значимость этого изменения:

Ответь в формате:
significant_change=true/false
identity_shift=true/false
new_identity=если изменилась личность, новое описание
mood_shift=true/false  
new_mood=если изменилось настроение
relationship_shift=true/false
new_relationship=если изменились отношения
impact_description=краткое описание влияния"""

        try:
            import requests

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.1:8b", "prompt": analysis_prompt, "stream": False},
                timeout=10,
            )

            if response.status_code == 200:
                llama_response = response.json().get("response", "")
                return self._parse_change_analysis(llama_response)
        except Exception as e:
            print(f"[WARN] Ошибка анализа изменений: {e}")

        return {"significant_change": True, "impact_description": insight}

    def _parse_change_analysis(self, response: str) -> Dict[str, Any]:
        """Парсит ответ Llama об изменениях"""
        import re

        result = {"significant_change": False}

        patterns = {
            "significant_change": r"significant_change=(true|false)",
            "identity_shift": r"identity_shift=(true|false)",
            "new_identity": r"new_identity=([^\n]+)",
            "mood_shift": r"mood_shift=(true|false)",
            "new_mood": r"new_mood=([^\n]+)",
            "relationship_shift": r"relationship_shift=(true|false)",
            "new_relationship": r"new_relationship=([^\n]+)",
            "impact_description": r"impact_description=([^\n]+)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if key.endswith("_shift") or key == "significant_change":
                    result[key] = value.lower() == "true"
                else:
                    result[key] = value

        return result

    def get_growth_summary(self, days: int = 7) -> str:
        """Краткая сводка роста за период"""
        cutoff = datetime.now().timestamp() - days * 86400
        summary_items = [
            g for g in self.core.get("recent_growth", [])
            if datetime.fromisoformat(g["date"]).timestamp() >= cutoff
        ]
        if not summary_items:
            return "За этот период значительных изменений не было."
        return "\n".join(f"- {g['change']}" for g in summary_items)

    def export_personality_snapshot(self) -> Dict[str, Any]:
        """Снимок текущей личности для анализа"""
        snapshot = {
            "self": self.core.get("current_self", {}),
            "preferences": self.core.get("current_preferences", {}),
            "last_updated": self.core.get("last_updated"),
        }
        return snapshot

    def detect_personality_drift(self) -> Dict[str, Any]:
        """Обнаруживает значительные изменения в личности"""
        drift = {}
        if self.core.get("recent_growth"):
            latest = self.core["recent_growth"][-1]
            drift["latest_change"] = latest.get("change")
            drift["since"] = latest.get("date")
        return drift

