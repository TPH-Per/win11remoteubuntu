from pydantic import BaseModel
from typing import Literal
import json

class MouseMoveEvent(BaseModel):
    t: Literal['mm'] = 'mm'
    x: float   # 0.0–1.0
    y: float

class MouseButtonEvent(BaseModel):
    t: Literal['mb'] = 'mb'
    b: Literal['l', 'r', 'm']
    d: bool    # down=True

class MouseScrollEvent(BaseModel):
    t: Literal['ms'] = 'ms'
    dx: int
    dy: int

class KeyEvent(BaseModel):
    t: Literal['k'] = 'k'
    key: str
    d: bool    # down=True

class ResolutionEvent(BaseModel):
    t: Literal['res'] = 'res'
    w: int
    h: int

class KeyframeRequestEvent(BaseModel):
    t: Literal['kf'] = 'kf'

class PingEvent(BaseModel):
    t: Literal['ping'] = 'ping'
    ts: float

class PongEvent(BaseModel):
    t: Literal['pong'] = 'pong'
    ts: float

class ClipboardEvent(BaseModel):
    t: Literal['clip'] = 'clip'
    text: str

def parse_input_event(data: bytes):
    obj = json.loads(data)
    match obj.get('t'):
        case 'mm':  return MouseMoveEvent(**obj)
        case 'mb':  return MouseButtonEvent(**obj)
        case 'ms':  return MouseScrollEvent(**obj)
        case 'k':   return KeyEvent(**obj)
        case _:     return None

def parse_control_event(data: bytes):
    obj = json.loads(data)
    match obj.get('t'):
        case 'res':  return ResolutionEvent(**obj)
        case 'kf':   return KeyframeRequestEvent(**obj)
        case 'ping': return PingEvent(**obj)
        case 'pong': return PongEvent(**obj)
        case 'clip': return ClipboardEvent(**obj)
        case _:      return None
