"""
Primary screen capture backend using python-mss.
"""

import mss
import numpy as np
import asyncio
from .base import CaptureBackend

class MssCapture(CaptureBackend):
    def __init__(self, monitor: int = 1):
        self._monitor_index = monitor
        self._sct = None
        self._monitor = None
        self._buf = None

    async def start(self) -> None:
        self._sct = mss.mss()
        self._monitor = self._sct.monitors[self._monitor_index]
        w, h = self._monitor['width'], self._monitor['height']
        self._buf = np.empty((h, w, 3), dtype=np.uint8)

    async def grab_frame(self) -> np.ndarray:
        screenshot = self._sct.grab(self._monitor)
        np.copyto(self._buf, np.array(screenshot)[..., :3])
        return self._buf

    async def stop(self) -> None:
        if self._sct:
            self._sct.close()

    @property
    def resolution(self) -> tuple[int, int]:
        if self._monitor is None:
            raise RuntimeError("Not started")
        return self._monitor['width'], self._monitor['height']
