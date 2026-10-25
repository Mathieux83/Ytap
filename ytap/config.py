import os

from platformdirs import user_config_path

CONFIG_DIR = user_config_path("ytap", appauthor=False)
API_KEY_FILE = CONFIG_DIR / "API_KEY"


def load_api_key():
    key = os.environ.get("YTAP_API_KEY", "").strip()
    if key:
        return key
    if API_KEY_FILE.is_file():
        return API_KEY_FILE.read_text(encoding="utf-8").strip()
    return ""


def save_api_key(key):
    key = key.strip()
    if not key:
        raise ValueError("The API key cannot be empty.")

    API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    API_KEY_FILE.write_text(f"{key}\n", encoding="utf-8")
    if os.name != "nt":
        API_KEY_FILE.chmod(0o600)
