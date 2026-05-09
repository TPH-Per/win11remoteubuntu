import socket
import logging
from shared.mux import FrameWriter, FrameDispatcher
from shared.protocol import STREAM_VIDEO, STREAM_INPUT, STREAM_CONTROL
from shared.events import parse_control_event, KeyframeRequestEvent
from ..decoder.h264 import H264Decoder
from ..renderer.pygame_window import PygameWindow
from ..kvm.focus import KVMFocusManager
from ..input.capture import InputCapture

logger = logging.getLogger(__name__)

class ThunderClient:
    def __init__(self, sock: socket.socket, fullscreen: bool = False):
        self._sock = sock
        self._fullscreen = fullscreen
        self._writer = FrameWriter(sock)
        self._decoder = H264Decoder()
        self._w = 1280
        self._h = 720
        self._window = None

    def run(self):
        import pygame
        
        # We need a dummy window getter for InputCapture before window exists
        def get_window_rect():
            return pygame.Rect(0, 0, self._w, self._h)

        def send_input(data):
            self._writer.write(STREAM_INPUT, data)

        input_capture = InputCapture(window_getter=get_window_rect, send_fn=send_input)
        kvm = KVMFocusManager(input_capture, self._w, self._h)
        
        # Start dispatcher
        dispatcher = FrameDispatcher(self._sock)
        dispatcher.on(STREAM_VIDEO, self._handle_video)
        dispatcher.on(STREAM_CONTROL, self._handle_control)
        dispatcher.start()
        
        self._window = PygameWindow(self._w, self._h, kvm, stats=None)
        self._window.start()
        
        # Wait for user or disconnect
        self._window.run_event_loop()

    def _handle_video(self, data: bytes):
        if not self._window: return
        frames = self._decoder.decode(data)
        for f in frames:
            self._window.push_frame(f)

    def _handle_control(self, data: bytes):
        event = parse_control_event(data)
        if event.t == 'res':
            self._w = event.w
            self._h = event.h
            if self._window:
                self._window.w = event.w
                self._window.h = event.h
        elif event.t == 'ping':
            pass
        elif event.t == 'clip':
            pass
