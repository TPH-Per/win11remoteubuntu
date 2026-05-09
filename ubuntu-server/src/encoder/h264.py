import av
import numpy as np

class H264Encoder:
    def __init__(self, width: int, height: int, fps: int = 60, bitrate_kbps: int = 4000):
        self.width = width
        self.height = height
        self.fps = fps
        self.bitrate_kbps = bitrate_kbps
        self._codec = None
        self._frame_count = 0
        self._force_next_keyframe = False
        self._build_codec()

    def _build_codec(self) -> None:
        codec = av.CodecContext.create('libx264', 'w')
        codec.width = self.width
        codec.height = self.height
        codec.time_base = av.Rational(1, self.fps)
        codec.pix_fmt = 'yuv420p'
        codec.bit_rate = self.bitrate_kbps * 1000
        codec.options = {
            'preset': 'ultrafast',
            'tune':   'zerolatency',
            'profile': 'baseline',
            'level': '4.1',
            'x264-params': 'nal-hrd=cbr:force-cfr=1:keyint=120:min-keyint=120',
        }
        codec.open()
        self._codec = codec

    def force_next_keyframe(self) -> None:
        self._force_next_keyframe = True

    def encode_frame(self, bgr: np.ndarray, force_keyframe: bool = False) -> bytes | None:
        frame = av.VideoFrame.from_ndarray(bgr[..., ::-1], format='rgb24')
        frame.pts = self._frame_count
        if force_keyframe or self._force_next_keyframe:
            frame.pict_type = av.video.frame.PictureType.I
            self._force_next_keyframe = False
        
        packets = self._codec.encode(frame)
        self._frame_count += 1
        
        if not packets:
            return None
        return b''.join(p.to_bytes() for p in packets)

    def flush(self) -> bytes:
        packets = self._codec.encode(None)
        return b''.join(p.to_bytes() for p in packets)
