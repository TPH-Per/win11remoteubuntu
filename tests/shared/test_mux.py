import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import socket
import threading
from shared.mux import FrameReader, FrameWriter
from shared.protocol import pack_frame, STREAM_INPUT

def test_frame_reader_handles_partial_recv():
    """FrameReader must assemble frame even if OS delivers data in 1-byte chunks."""
    payload = b'test_payload_1234'
    frame_bytes = pack_frame(STREAM_INPUT, payload)
    
    # Simulate socket that delivers 1 byte at a time
    class SlowSocket:
        def __init__(self, data):
            self._data = iter(data)
        def recv(self, n):
            try:
                return bytes([next(self._data)])
            except StopIteration:
                return b''
    
    reader = FrameReader(SlowSocket(frame_bytes))
    sid, received = reader.read_frame()
    assert sid == STREAM_INPUT
    assert received == payload

def test_frame_writer_thread_safety():
    """Concurrent writes from 10 threads must not interleave frame headers."""
    received_frames = []
    lock = threading.Lock()
    
    server_sock, client_sock = socket.socketpair()
    writer = FrameWriter(client_sock)
    reader = FrameReader(server_sock)
    
    def read_all():
        for _ in range(10):
            sid, data = reader.read_frame()
            with lock:
                received_frames.append((sid, data))
    
    reader_thread = threading.Thread(target=read_all)
    reader_thread.start()
    
    threads = []
    for i in range(10):
        payload = f'thread_{i}'.encode()
        t = threading.Thread(target=writer.write, args=(STREAM_INPUT, payload))
        threads.append(t)
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    reader_thread.join(timeout=5)
    
    assert len(received_frames) == 10
    # All payloads must be intact (no interleaving)
    payloads = {data for _, data in received_frames}
    assert payloads == {f'thread_{i}'.encode() for i in range(10)}
