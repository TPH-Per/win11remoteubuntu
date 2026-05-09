import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.protocol import pack_frame, unpack_header, STREAM_VIDEO, STREAM_INPUT, STREAM_CONTROL, HEADER_SIZE

def test_pack_unpack_roundtrip():
    """pack_frame then unpack_header must recover original values."""
    payload = b'hello world'
    frame = pack_frame(STREAM_VIDEO, payload)
    
    assert len(frame) == HEADER_SIZE + len(payload)
    
    sid, length = unpack_header(frame[:HEADER_SIZE])
    assert sid == STREAM_VIDEO
    assert length == len(payload)
    assert frame[HEADER_SIZE:] == payload

def test_pack_frame_all_stream_ids():
    for sid in [STREAM_VIDEO, STREAM_INPUT, STREAM_CONTROL]:
        frame = pack_frame(sid, b'\x00' * 10)
        recovered_sid, _ = unpack_header(frame[:HEADER_SIZE])
        assert recovered_sid == sid

def test_empty_payload():
    frame = pack_frame(STREAM_CONTROL, b'')
    sid, length = unpack_header(frame[:HEADER_SIZE])
    assert length == 0

def test_large_payload():
    payload = b'\xFF' * (1024 * 1024)  # 1MB
    frame = pack_frame(STREAM_VIDEO, payload)
    _, length = unpack_header(frame[:HEADER_SIZE])
    assert length == 1024 * 1024
