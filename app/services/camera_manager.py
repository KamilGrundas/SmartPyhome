import re
import threading
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote

from app.services.camera_runtime import RTSPCamera
from app.core.config import settings


def _creds() -> str:
    return f"{quote(settings.CAM_USER, safe='')}:{quote(settings.CAM_PASS, safe='')}"


def _paths() -> List[str]:
    base = ["/stream1", "/stream2", "/stream3"]
    primary = settings.RTSP_PATH if settings.RTSP_PATH else None
    if primary and not primary.startswith("/"):
        primary = f"/{primary}"
    if primary in base:
        return [primary] + [p for p in base if p != primary]
    return base


_SANITIZE_RE = re.compile(r"[^a-zA-Z0-9._\- ]+")


def _safe_name(name: str) -> str:
    s = _SANITIZE_RE.sub("", name).strip()
    s = re.sub(r"\s+", "_", s)
    return s or "camera"


class CameraManager:
    def __init__(self) -> None:
        self._cams: Dict[str, RTSPCamera] = {}
        self._lock = threading.Lock()
        self._root = Path(settings.RECORD_DIR).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def _build_urls(self, ip: str) -> List[str]:
        creds = _creds()
        return [f"rtsp://{creds}@{ip}:554{p}" for p in _paths()]

    def ensure(self, camera_name: str, ip: str) -> RTSPCamera:
        key = camera_name
        if key in self._cams:
            return self._cams[key]
        with self._lock:
            if key in self._cams:
                return self._cams[key]
            urls = self._build_urls(ip)
            rec_dir = self._root / _safe_name(camera_name)
            cam = RTSPCamera(urls, record_dir=rec_dir)
            cam.start()
            self._cams[key] = cam
            return cam

    def stop_all(self) -> None:
        with self._lock:
            for cam in self._cams.values():
                try:
                    cam.stop()
                except Exception:
                    pass
            self._cams.clear()
