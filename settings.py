import json
import os
import sys

DEFAULTS = {
    "ui_language": "fa",
    "ocr_lang": "fas+eng",
    "psm": "3",
    "preprocess": True,
    "binarize": False,
    "auto_psm": True,
    "show_preprocessed": False,
    "export_format": "txt",
    "ocr_mode": "accurate",
}


def get_config_path():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "settings.json")


def load_settings():
    path = get_config_path()
    data = dict(DEFAULTS)
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                data.update({k: stored[k] for k in DEFAULTS if k in stored})
        except (json.JSONDecodeError, OSError):
            pass
    return data


def save_settings(data):
    path = get_config_path()
    payload = {k: data.get(k, DEFAULTS[k]) for k in DEFAULTS}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
