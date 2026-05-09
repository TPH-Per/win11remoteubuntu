"""
All JSON events sent over STREAM_INPUT and STREAM_CONTROL.
Kept minimal — small JSON = fast serialization over TCP.
"""

from pydantic import BaseModel
from typing import Literal
import json

# ── INPUT EVENTS (Windows → Ubuntu, stream 0x02) ──────────────────────

class MouseMoveEvent(BaseModel):
    t: Literal['mm'] = 'mm'
    x: float
    y: float

class MouseButtonEvent(BaseModel):
    t: Literal['mb'] = 'mb'
    b: Literal['l', 'r', 'm']
    d: bool

class MouseScrollEvent(BaseModel):
    t: Literal['ms'] = 'ms'
    dx: int
    dy: int

class KeyEvent(BaseModel):
    t: Literal['k'] = 'k'
    key: str
    d: bool

# ── CONTROL EVENTS (bidirectional, stream 0x03) ────────────────────────

class ClipboardEvent(BaseModel):
    t: Literal['clip'] = 'clip'
    text: str

class PingEvent(BaseModel):
    t: Literal['ping'] = 'ping'
    ts: float

class PongEvent(BaseModel):
    t: Literal['pong'] = 'pong'
    ts: float

class KeyframeRequestEvent(BaseModel):
    t: Literal['kf'] = 'kf'

class ResolutionEvent(BaseModel):
    t: Literal['res'] = 'res'
    w: int
    h: int

# ── Deserialization helpers ────────────────────────────────────────────

_INPUT_MAP = {'mm': MouseMoveEvent, 'mb': MouseButtonEvent,
               'ms': MouseScrollEvent, 'k': KeyEvent}

_CONTROL_MAP = {'clip': ClipboardEvent, 'ping': PingEvent,
                 'pong': PongEvent, 'kf': KeyframeRequestEvent,
                 'res': ResolutionEvent}

def parse_input_event(data: bytes):
    obj = json.loads(data)
    cls = _INPUT_MAP.get(obj.get('t'))
    if cls is None:
        raise ValueError(f"Unknown input event: {obj.get('t')}")
    return cls(**obj)

def parse_control_event(data: bytes):
    obj = json.loads(data)
    cls = _CONTROL_MAP.get(obj.get('t'))
    if cls is None:
        raise ValueError(f"Unknown control event: {obj.get('t')}")
    return cls(**obj)
