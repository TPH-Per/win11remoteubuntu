import av
import numpy as np

class H264Decoder:
    def __init__(self):
        self._codec = None
        self._waiting_for_keyframe = True
        self.reset()
        
    def decode(self, packet_bytes: bytes) -> list[np.ndarray]:
        frames = []
        try:
            packets = self._codec.parse(packet_bytes)
            for packet in packets:
                if self._waiting_for_keyframe:
                    if not packet.is_keyframe:
                        continue
                    self._waiting_for_keyframe = False
                
                for frame in self._codec.decode(packet):
                    frames.append(frame.to_ndarray(format='rgb24'))
        except Exception:
            self.reset()
            return []
        return frames

    def reset(self):
        self._codec = av.CodecContext.create('h264', 'r')
        self._waiting_for_keyframe = True
