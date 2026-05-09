import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.encoder.h264 import H264Encoder

def test_encoder_output_decodable():
    enc = H264Encoder(width=640, height=480, fps=30)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    packets = [enc.encode_frame(frame, force_keyframe=(i==0)) for i in range(10)]
    packets = [p for p in packets if p is not None]
    assert len(packets) > 0, "Encoder produced no output"

def test_keyframe_is_idr():
    enc = H264Encoder(width=640, height=480, fps=30)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    for _ in range(3):
        enc.encode_frame(frame, force_keyframe=False)
    
    pkt = enc.encode_frame(frame, force_keyframe=True)
    assert pkt is not None
    
    found_idr = False
    i = 0
    while i < len(pkt) - 4:
        if pkt[i:i+4] == b'\x00\x00\x00\x01':
            nal_type = pkt[i+4] & 0x1F
            if nal_type == 5:
                found_idr = True
                break
            i += 4
        elif pkt[i:i+3] == b'\x00\x00\x01':
            nal_type = pkt[i+3] & 0x1F
            if nal_type == 5:
                found_idr = True
                break
            i += 3
        else:
            i += 1
    
    assert found_idr, "No IDR NAL unit found in forced keyframe packet"
