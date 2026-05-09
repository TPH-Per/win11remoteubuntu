"""
Binary framing protocol for TCP multiplexing.
Every message over the TCP socket uses this 5-byte header:

  +----------+-----------+------------------------------+
  | stream_id | length    | payload                     |
  | (1 byte)  | (4 bytes) | (variable)                  |
  +----------+-----------+------------------------------+

stream_id constants:
  STREAM_VIDEO   = 0x01   H.264 NAL unit bytes (binary)
  STREAM_INPUT   = 0x02   JSON-encoded InputEvent (UTF-8)
  STREAM_CONTROL = 0x03   JSON-encoded ControlEvent (UTF-8)

HEADER_FORMAT = '!BI'  (network byte order: unsigned char + unsigned int)
HEADER_SIZE   = 5
MAX_PAYLOAD   = 8 * 1024 * 1024   (8 MB safety limit)
"""

import struct

STREAM_VIDEO   = 0x01
STREAM_INPUT   = 0x02
STREAM_CONTROL = 0x03

HEADER_FORMAT = '!BI'
HEADER_SIZE   = struct.calcsize(HEADER_FORMAT)  # = 5 bytes
MAX_PAYLOAD   = 8 * 1024 * 1024

def pack_frame(stream_id: int, payload: bytes) -> bytes:
    """Serialize one frame with header."""
    header = struct.pack(HEADER_FORMAT, stream_id, len(payload))
    return header + payload

def unpack_header(header_bytes: bytes) -> tuple[int, int]:
    """Returns (stream_id, payload_length) from 5-byte header."""
    return struct.unpack(HEADER_FORMAT, header_bytes)
