from pynput import mouse as pmouse, keyboard as pkeyboard
from shared.events import MouseMoveEvent, MouseButtonEvent, MouseScrollEvent, KeyEvent

SPECIAL_KEY_MAP = {
    'enter':     pkeyboard.Key.enter,
    'shift':     pkeyboard.Key.shift,
    'ctrl':      pkeyboard.Key.ctrl_l,
    'alt':       pkeyboard.Key.alt_l,
    'tab':       pkeyboard.Key.tab,
    'escape':    pkeyboard.Key.esc,
    'backspace': pkeyboard.Key.backspace,
    'delete':    pkeyboard.Key.delete,
    'space':     pkeyboard.Key.space,
    'up':        pkeyboard.Key.up,
    'down':      pkeyboard.Key.down,
    'left':      pkeyboard.Key.left,
    'right':     pkeyboard.Key.right,
    'super':     pkeyboard.Key.cmd,
    'caps_lock': pkeyboard.Key.caps_lock
}
for i in range(1, 13):
    SPECIAL_KEY_MAP[f'f{i}'] = getattr(pkeyboard.Key, f'f{i}')

BUTTON_MAP = {
    'l': pmouse.Button.left,
    'r': pmouse.Button.right,
    'm': pmouse.Button.middle,
}

class InputExecutor:
    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._mouse = pmouse.Controller()
        self._keyboard = pkeyboard.Controller()

    def execute(self, event) -> None:
        match type(event).__name__:
            case 'MouseMoveEvent':   self._mouse_move(event)
            case 'MouseButtonEvent': self._mouse_button(event)
            case 'MouseScrollEvent': self._mouse_scroll(event)
            case 'KeyEvent':         self._key(event)
            case _: pass

    def _mouse_move(self, e: MouseMoveEvent) -> None:
        x = int(max(0.0, min(1.0, e.x)) * self.screen_w)
        y = int(max(0.0, min(1.0, e.y)) * self.screen_h)
        self._mouse.position = (x, y)

    def _mouse_button(self, e: MouseButtonEvent) -> None:
        btn = BUTTON_MAP.get(e.b)
        if not btn: return
        if e.d:
            self._mouse.press(btn)
        else:
            self._mouse.release(btn)

    def _mouse_scroll(self, e: MouseScrollEvent) -> None:
        self._mouse.scroll(e.dx, e.dy)

    def _key(self, e: KeyEvent) -> None:
        key = SPECIAL_KEY_MAP.get(e.key, e.key)
        if e.d:
            self._keyboard.press(key)
        else:
            self._keyboard.release(key)
