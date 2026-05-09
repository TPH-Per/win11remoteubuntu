import socket
import threading
import time
import logging
import asyncio
from shared.mux import FrameWriter, FrameDispatcher
from shared.protocol import STREAM_VIDEO, STREAM_INPUT, STREAM_CONTROL
from shared.events import ResolutionEvent, parse_input_event, parse_control_event
from ..capture.mss_capture import MssCapture
from ..encoder.h264 import H264Encoder
from ..input.executor import InputExecutor

logger = logging.getLogger(__name__)

def capture_sync_start(capture):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(capture.start())
    loop.close()

def capture_sync_grab(capture):
    loop = asyncio.new_event_loop()
    res = loop.run_until_complete(capture.grab_frame())
    loop.close()
    return res

class ThunderServer:
    def __init__(self, host: str, port: int, fps: int, bitrate_kbps: int, executor_factory=None):
        self.host = host
        self.port = port
        self.fps = fps
        self.bitrate_kbps = bitrate_kbps
        self._running = False
        self.executor_factory = executor_factory

    def serve_forever(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            srv.bind((self.host, self.port))
            srv.listen(1)
            logger.info(f"ThunderKVM server listening on {self.host}:{self.port}")
            
            while True:
                conn, addr = srv.accept()
                logger.info(f"Viewer connected from {addr}")
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                try:
                    self._handle_client(conn)
                except ConnectionError as e:
                    logger.info(f"Viewer disconnected: {e}")
                finally:
                    conn.close()
                    logger.info("Waiting for next viewer connection...")
                    
    def serve_once(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            srv.bind((self.host, self.port))
            srv.listen(1)
            conn, _ = srv.accept()
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            try:
                self._handle_client(conn)
            except ConnectionError:
                pass
            finally:
                conn.close()

    def _handle_client(self, conn: socket.socket) -> None:
        capture = MssCapture(monitor=1)
        capture_sync_start(capture)
        
        w, h = capture.resolution
        encoder = H264Encoder(width=w, height=h, fps=self.fps, bitrate_kbps=self.bitrate_kbps)
        if self.executor_factory:
            executor = self.executor_factory(w, h)
        else:
            executor = InputExecutor(screen_w=w, screen_h=h)
        writer = FrameWriter(conn)
        
        res_event = ResolutionEvent(w=w, h=h)
        writer.write(STREAM_CONTROL, res_event.model_dump_json().encode())
        
        dispatcher = FrameDispatcher(conn)
        dispatcher.on(STREAM_INPUT,   lambda data: executor.execute(parse_input_event(data)))
        dispatcher.on(STREAM_CONTROL, lambda data: self._handle_control(data, writer, encoder))
        dispatcher.start()
        
        self._capture_loop(capture, encoder, writer)

    def _capture_loop(self, capture, encoder, writer: FrameWriter) -> None:
        frame_interval = 1.0 / self.fps
        force_keyframe = True
        
        while True:
            t_start = time.monotonic()
            
            frame_bgr = capture_sync_grab(capture)
            encoded = encoder.encode_frame(frame_bgr, force_keyframe=force_keyframe)
            force_keyframe = False
            
            if encoded:
                try:
                    writer.write(STREAM_VIDEO, encoded)
                except ConnectionError:
                    break
            
            elapsed = time.monotonic() - t_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _handle_control(self, data: bytes, writer: FrameWriter, encoder: H264Encoder) -> None:
        event = parse_control_event(data)
        match event.t:
            case 'kf':
                encoder.force_next_keyframe()
            case 'ping':
                from shared.events import PongEvent
                pong = PongEvent(ts=event.ts)
                writer.write(STREAM_CONTROL, pong.model_dump_json().encode())
            case 'clip':
                try:
                    import pyperclip
                    pyperclip.copy(event.text)
                except ImportError:
                    pass
