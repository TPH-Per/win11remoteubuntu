import av
import numpy as np

class H264Decoder:
    def __init__(self):
        self._codec = av.CodecContext.create('h264', 'r')
        
    def decode(self, packet_bytes: bytes) -> list[np.ndarray]:
        packets = self._codec.parse(packet_bytes)
        frames = []
        for packet in packets:
            for frame in self._codec.decode(packet):
                frames.append(frame.to_ndarray(format='rgb24'))
        return frames
