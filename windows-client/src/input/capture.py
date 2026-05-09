import time
import json
from pynput import mouse as pmouse, keyboard as pkeyboard
from shared.events import MouseMoveEvent, MouseButtonEvent, MouseScrollEvent, KeyEvent

class InputCapture:
    def __init__(self, window_getter, send_fn):
        self._window_getter = window_getter
        self._send_fn = send_fn
        self._mouse_listener = None
        self._keyboard_listener = None
        self._running = False
        self._last_mouse_move = 0
        self._rate_limit = 1.0 / 60

    def start(self):
        if self._running: return
        self._running = True
        self._mouse_listener = pmouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll,
            suppress=True
        )
        self._keyboard_listener = pkeyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
            suppress=True
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self):
        if not self._running: return
        self._running = False
        if self._mouse_listener: self._mouse_listener.stop()
        if self._keyboard_listener: self._keyboard_listener.stop()

    def _on_mouse_move(self, x, y):
        now = time.monotonic()
        if now - self._last_mouse_move < self._rate_limit:
            return
        self._last_mouse_move = now
        rect = self._window_getter()
        if not rect: return
        
        rel_x = (x - getattr(rect, 'x', 0)) / rect.width
        rel_y = (y - getattr(rect, 'y', 0)) / rect.height
        
        rel_x = max(0.0, min(1.0, rel_x))
        rel_y = max(0.0, min(1.0, rel_y))
        
        event = MouseMoveEvent(x=rel_x, y=rel_y)
        self._send_fn(event.model_dump_json().encode())

    def _on_mouse_click(self, x, y, button, pressed):
        btn_map = {pmouse.Button.left: 'l', pmouse.Button.right: 'r', pmouse.Button.middle: 'm'}
        if button in btn_map:
            event = MouseButtonEvent(b=btn_map[button], d=pressed)
            self._send_fn(event.model_dump_json().encode())

    def _on_mouse_scroll(self, x, y, dx, dy):
        event = MouseScrollEvent(dx=int(dx), dy=int(dy))
        self._send_fn(event.model_dump_json().encode())

    def _key_name(self, key):
        if hasattr(key, 'char') and key.char is not None:
            return key.char
        return key.name

    def _on_key_press(self, key):
        k_str = self._key_name(key)
        if k_str:
            event = KeyEvent(key=k_str, d=True)
            self._send_fn(event.model_dump_json().encode())

    def _on_key_release(self, key):
        k_str = self._key_name(key)
        if k_str:
            event = KeyEvent(key=k_str, d=False)
            self._send_fn(event.model_dump_json().encode())
