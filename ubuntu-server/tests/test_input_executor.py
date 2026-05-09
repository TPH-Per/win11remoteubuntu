import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from unittest.mock import patch, PropertyMock, MagicMock
from src.input.executor import InputExecutor
from shared.events import MouseMoveEvent, MouseButtonEvent, KeyEvent

def test_mouse_move_center():
    exec = InputExecutor(screen_w=1920, screen_h=1080)
    with patch.object(exec._mouse, 'position', new_callable=PropertyMock) as pos:
        exec.execute(MouseMoveEvent(x=0.5, y=0.5))
        pos.assert_called_with((960, 540))

def test_mouse_move_clamps_negative():
    exec = InputExecutor(screen_w=1920, screen_h=1080)
    with patch.object(exec._mouse, 'position', new_callable=PropertyMock) as pos:
        exec.execute(MouseMoveEvent(x=-0.5, y=-0.5))
        pos.assert_called_with((0, 0))

def test_unknown_event_does_not_crash():
    exec = InputExecutor(screen_w=1920, screen_h=1080)
    class UnknownEvent:
        pass
    exec.execute(UnknownEvent())  # Must not raise
