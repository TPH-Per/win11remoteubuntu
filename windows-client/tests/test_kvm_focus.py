import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from unittest.mock import MagicMock, patch
import pygame
from src.kvm.focus import KVMFocusManager, KVMState

def make_scroll_lock_event():
    evt = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SCROLLOCK, 'mod': 0, 'unicode': ''})
    return evt

def test_initial_state_is_local():
    kvm = KVMFocusManager(input_capture=MagicMock(), window_w=1280, window_h=720)
    assert kvm.state == KVMState.FOCUSED_LOCAL

@patch('pygame.event.set_grab')
@patch('pygame.mouse.set_visible')
def test_debounce_prevents_double_toggle(mock_set_visible, mock_set_grab):
    capture = MagicMock()
    kvm = KVMFocusManager(capture, 1280, 720)
    kvm.handle_key(make_scroll_lock_event())
    kvm.handle_key(make_scroll_lock_event())  # Within 200ms
    assert kvm.state == KVMState.FOCUSED_REMOTE

@patch('pygame.event.set_grab')
@patch('pygame.mouse.set_visible')
def test_other_keys_ignored(mock_set_visible, mock_set_grab):
    kvm = KVMFocusManager(MagicMock(), 1280, 720)
    evt = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a, 'mod': 0, 'unicode': 'a'})
    consumed = kvm.handle_key(evt)
    assert not consumed
    assert kvm.state == KVMState.FOCUSED_LOCAL
