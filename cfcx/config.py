from functools import lru_cache
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "configs"


@lru_cache
def load_config(name: str) -> dict:
    with open(CONFIG_DIR / f"{name}.yaml") as f:
        return yaml.safe_load(f)


def leagues() -> list[dict]:
    return load_config("leagues")["leagues"]


def seasons() -> list[str]:
    return load_config("leagues")["seasons"]


def data_config() -> dict:
    return load_config("data")
