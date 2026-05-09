import time
import pygame
from enum import Enum, auto

class KVMState(Enum):
    FOCUSED_LOCAL  = auto()
    FOCUSED_REMOTE = auto()

class KVMFocusManager:
    TOGGLE_COOLDOWN_MS = 200

    def __init__(self, input_capture, window_w: int, window_h: int):
        self._capture = input_capture
        self._state = KVMState.FOCUSED_LOCAL
        self._last_toggle = 0
        self._window_w = window_w
        self._window_h = window_h

    @property
    def state(self) -> KVMState:
        return self._state

    def handle_key(self, pygame_event) -> bool:
        """
        Call from pygame event loop.
        Returns True if event was consumed (is the toggle hotkey).
        """
        if pygame_event.type != pygame.KEYDOWN:
            return False
        if pygame_event.key != pygame.K_SCROLLOCK:   # configurable
            return False
        
        now = time.monotonic() * 1000
        if now - self._last_toggle < self.TOGGLE_COOLDOWN_MS:
            return True  # Debounce
        
        self._last_toggle = now
        self._toggle()
        return True

    def _toggle(self) -> None:
        if self._state == KVMState.FOCUSED_LOCAL:
            self._enter_remote()
        else:
            self._enter_local()

    def _enter_remote(self) -> None:
        self._state = KVMState.FOCUSED_REMOTE
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self._capture.start()

    def _enter_local(self) -> None:
        self._state = KVMState.FOCUSED_LOCAL
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        self._capture.stop()
