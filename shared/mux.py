import struct, socket, threading

# Frame format: [1 byte stream_id][4 bytes length BE][N bytes data]
HEADER_FMT = '>BI'
HEADER_SIZE = struct.calcsize(HEADER_FMT)   # = 5 bytes

class FrameWriter:
    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._lock = threading.Lock()

    def write(self, stream_id: int, data: bytes) -> None:
        header = struct.pack(HEADER_FMT, stream_id, len(data))
        with self._lock:
            self._sock.sendall(header + data)

class FrameDispatcher:
    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._handlers: dict = {}
        self._thread = None

    def on(self, stream_id: int, handler) -> None:
        self._handlers[stream_id] = handler

    def start(self) -> None:
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def _recv_loop(self) -> None:
        while True:
            try:
                header = self._recvall(HEADER_SIZE)
                if not header:
                    break
                stream_id, length = struct.unpack(HEADER_FMT, header)
                data = self._recvall(length)
                if not data:
                    break
                handler = self._handlers.get(stream_id)
                if handler:
                    handler(data)
            except (ConnectionError, OSError):
                break

    def _recvall(self, n: int) -> bytes | None:
        buf = bytearray()
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                return None
            buf.extend(chunk)
        return bytes(buf)
