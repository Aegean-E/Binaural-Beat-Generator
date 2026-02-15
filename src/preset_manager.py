import json
from pathlib import Path
import presets

APP_DIR = Path.home() / ".binaural_beat_generator"
CONFIG_PATH = APP_DIR / "config.json"

class PresetManager:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> dict:
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def save_config(self) -> None:
        try:
            APP_DIR.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(self.config, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_theme(self) -> str:
        return self.config.get("theme", "darkly")

    def set_theme(self, theme_name: str) -> None:
        self.config["theme"] = theme_name
        self.save_config()

    def _normalize_category(self, category: str) -> str:
        c = str(category).strip().lower()
        if c == "binaural":
            return "Binaural"
        if c == "monaural":
            return "Monaural"
        raise ValueError("Category must be 'Monaural' or 'Binaural'")

    def get_user_presets(self) -> dict:
        up = self.config.get("user_presets", {})
        # Ensure structure
        return {
            "Monaural": list(up.get("Monaural", [])),
            "Binaural": list(up.get("Binaural", [])),
        }

    def add_user_preset(self, category: str, label: str, left_hz: float, right_hz: float) -> None:
        category = self._normalize_category(category)
        label = str(label).strip()
        if not label:
            raise ValueError("Preset Name Cannot be Empty")

        preset_obj = {
            "label": label,
            "left_hz": float(left_hz),
            "right_hz": float(right_hz),
        }

        up = self.get_user_presets()
        # Check if exists, maybe overwrite?
        # For now, just append, or maybe prevent duplicates?
        # Original code just appended. I'll check for duplicates by name to be safe.
        existing_idx = next((i for i, p in enumerate(up[category]) if p["label"] == label), -1)

        if existing_idx >= 0:
            up[category][existing_idx] = preset_obj
        else:
            up[category].append(preset_obj)

        self.config["user_presets"] = up
        self.save_config()

    def remove_user_preset(self, category: str, label: str) -> bool:
        category = self._normalize_category(category)
        up = self.get_user_presets()
        label = str(label).strip()

        for i, p in enumerate(up[category]):
            if str(p.get("label", "")).strip() == label:
                up[category].pop(i)
                self.config["user_presets"] = up
                self.save_config()
                return True
        return False

    def get_all_presets(self) -> dict:
        up = self.get_user_presets()
        return {
            "Monaural": list(presets.MONAURAL_PRESETS) + up["Monaural"],
            "Binaural": list(presets.BINAURAL_PRESETS) + up["Binaural"],
        }

    def import_config(self, filepath: str):
        imported = json.loads(Path(filepath).read_text(encoding="utf-8"))
        if not isinstance(imported, dict):
            raise ValueError("Invalid config file: root JSON value must be an object.")

        # Normalize user_presets shape so UI won't crash
        up = imported.get("user_presets", {})
        if not isinstance(up, dict):
            up = {}

        imported["user_presets"] = {
            "Monaural": list((up.get("Monaural") or [])) if isinstance(up.get("Monaural"), list) else [],
            "Binaural": list((up.get("Binaural") or [])) if isinstance(up.get("Binaural"), list) else [],
        }

        self.config = imported
        self.save_config()

    def export_config(self, filepath: str):
        Path(filepath).write_text(json.dumps(self.config, indent=2), encoding="utf-8")
