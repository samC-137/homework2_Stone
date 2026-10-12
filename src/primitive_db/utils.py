import json
from pathlib import Path

from primitive_db.constants import DATA_DIR


def load_metadata(filepath: str | Path) -> dict:
    path = Path(filepath)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_metadata(filepath: str | Path, metadata: dict) -> None:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def table_path(table_name: str) -> Path:
    return DATA_DIR / f"{table_name}.json"


def load_table_data(table_name: str) -> list[dict]:
    path = table_path(table_name)
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def save_table_data(table_name: str, rows: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    table_path(table_name).write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
