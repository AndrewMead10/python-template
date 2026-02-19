import uuid
from pathlib import Path

from app.config import settings


def get_storage_path(key: str) -> Path:
    storage = Path(settings.storage_path)
    storage.mkdir(parents=True, exist_ok=True)
    return storage / key


async def save_file(key: str, content: bytes) -> str:
    path = get_storage_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return key


def generate_key(prefix: str = "", suffix: str = "") -> str:
    return f"{prefix}{uuid.uuid4()}{suffix}"


def delete_file(key: str) -> bool:
    path = get_storage_path(key)
    if path.exists():
        path.unlink()
        return True
    return False
