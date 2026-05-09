import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.input.capture import InputCapture
import pygame
import json

def test_mouse_coords_normalized_to_window():
    sent = []
    window_getter = lambda: pygame.Rect(200, 100, 1280, 720)
    cap = InputCapture(window_getter=window_getter, send_fn=lambda d: sent.append(json.loads(d)))
    
    cap._on_mouse_move(840, 460)
    assert abs(sent[0]['x'] - 0.5) < 0.005
    assert abs(sent[0]['y'] - 0.5) < 0.005

def test_mouse_outside_window_clamped():
    sent = []
    window_getter = lambda: pygame.Rect(200, 100, 1280, 720)
    cap = InputCapture(window_getter=window_getter, send_fn=lambda d: sent.append(json.loads(d)))
    cap._on_mouse_move(0, 0)
    assert sent[0]['x'] == 0.0
    assert sent[0]['y'] == 0.0
