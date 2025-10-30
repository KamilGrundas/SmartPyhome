import threading
import time
from typing import Optional, List, Tuple
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np

from app.core.config import settings


class RTSPCamera:
    def __init__(self, urls: List[str], record_dir: Path):
        assert urls, "RTSPCamera: expected at least one URL"
        self.urls = urls
        self.idx = 0

        self.cap: Optional[cv2.VideoCapture] = None
        self.lock = threading.Lock()
        self.frame: Optional[np.ndarray] = None

        self.record_enabled = bool(settings.RECORD_ENABLED)
        self.record_dir = record_dir
        if self.record_enabled:
            self.record_dir.mkdir(parents=True, exist_ok=True)
        self.writer: Optional[cv2.VideoWriter] = None
        self.segment_started_at: float = 0.0
        self.out_size: Optional[Tuple[int, int]] = None
        self.fps: float = settings.RECORD_FPS_FALLBACK
        self.fourcc = cv2.VideoWriter_fourcc(*settings.RECORD_CODEC)  # type: ignore

        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self._release()
        self._release_writer()

    def _open_any(self) -> bool:
        self._release()
        n = len(self.urls)
        start = self.idx
        for step in range(n):
            i = (start + step) % n
            url = self.urls[i]
            self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
            if self.cap.isOpened():
                self.idx = i
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                if fps and fps > 0:
                    self.fps = float(fps)
                else:
                    self.fps = settings.RECORD_FPS_FALLBACK
                return True
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
            time.sleep(0.2)
        return False

    def _release(self) -> None:
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def _release_writer(self) -> None:
        if self.writer is not None:
            try:
                self.writer.release()
            except Exception:
                pass
            self.writer = None

    def _ensure_writer(self, frame: np.ndarray) -> None:
        if not self.record_enabled:
            return
        h, w = frame.shape[:2]
        size = (w, h)
        if self.out_size != size:
            self._release_writer()
            self.out_size = size
            self.segment_started_at = 0.0

        now = time.time()
        if (self.writer is None) or (
            now - self.segment_started_at >= settings.RECORD_SEGMENT_SECONDS
        ):
            self._release_writer()
            name = f"video_{datetime.now().strftime('%d_%m_%Y_%H_%M')}"
            out_path = self.record_dir / f"{name}.mp4"
            self.writer = cv2.VideoWriter(
                str(out_path),
                self.fourcc,
                self.fps,
                self.out_size,  # type: ignore
            )
            self.segment_started_at = now

    def _loop(self) -> None:
        backoff = 0.5
        while self.running:
            try:
                if self.cap is None or not self.cap.isOpened():
                    if not self._open_any():
                        time.sleep(min(backoff, 5.0))
                        backoff = min(backoff * 2, 5.0)
                        continue

                ok, frame = self.cap.read()  # type: ignore
                if ok and frame is not None:
                    with self.lock:
                        self.frame = frame
                    try:
                        if self.record_enabled:
                            self._ensure_writer(frame)
                            if self.writer is not None:
                                self.writer.write(frame)
                    except Exception:
                        pass
                    backoff = 0.5
                else:
                    self._release()
                    time.sleep(0.25)
            except Exception:
                self._release()
                time.sleep(0.5)

    def get_jpeg(self, quality: int = 80) -> Optional[bytes]:
        with self.lock:
            if self.frame is None:
                return None
            ok, jpg = cv2.imencode(
                ".jpg", self.frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            )
        if not ok:
            return None
        return jpg.tobytes()
