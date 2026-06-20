from __future__ import annotations

from threading import Lock
from typing import Any, Dict, Optional

_lock = Lock()
_latest: Optional[Dict[str, Any]] = None


def store(payload: Optional[Dict[str, Any]]) -> None:
    global _latest
    with _lock:
        _latest = payload


def latest() -> Optional[Dict[str, Any]]:
    with _lock:
        return dict(_latest) if _latest is not None else None
