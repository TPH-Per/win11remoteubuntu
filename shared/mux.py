"""
TCPMux: a framed reader/writer over a raw TCP socket.
"""

import socket
import struct
import threading
from typing import Callable
from .protocol import HEADER_SIZE, HEADER_FORMAT, MAX_PAYLOAD, unpack_header

class FrameWriter:
    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._lock = threading.Lock()

    def write(self, stream_id: int, payload: bytes) -> None:
        """Thread-safe: pack and send one frame."""
        header = struct.pack(HEADER_FORMAT, stream_id, len(payload))
        with self._lock:
            self._sock.sendall(header + payload)

class FrameReader:
    def __init__(self, sock: socket.socket):
        self._sock = sock

    def read_frame(self) -> tuple[int, bytes]:
        """
        Blocking. Reads exactly one frame.
        Raises ConnectionError if socket closes.
        """
        header = self._recv_exactly(HEADER_SIZE)
        stream_id, length = unpack_header(header)
        if length > MAX_PAYLOAD:
            raise ValueError(f"Frame too large: {length} bytes")
        payload = self._recv_exactly(length)
        return stream_id, payload

    def _recv_exactly(self, n: int) -> bytes:
        buf = bytearray()
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("Socket closed")
            buf.extend(chunk)
        return bytes(buf)

class FrameDispatcher:
    def __init__(self, sock: socket.socket):
        self._reader = FrameReader(sock)
        self._callbacks: dict[int, list[Callable]] = {}
        self._thread = threading.Thread(target=self._run, daemon=True)

    def on(self, stream_id: int, callback: Callable[[bytes], None]) -> None:
        self._callbacks.setdefault(stream_id, []).append(callback)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        while True:
            try:
                stream_id, payload = self._reader.read_frame()
                for cb in self._callbacks.get(stream_id, []):
                    cb(payload)
            except ConnectionError:
                break
