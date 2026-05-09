import pytest
import asyncio
import numpy as np
import subprocess
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.capture.mss_capture import MssCapture

@pytest.fixture(scope='session')
def xvfb():
    """Start a virtual X11 display for headless testing."""
    proc = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1280x720x24'])
    yield ':99'
    proc.terminate()

def test_mss_capture_shape(xvfb, monkeypatch):
    monkeypatch.setenv('DISPLAY', xvfb)
    cap = MssCapture(monitor=1)
    asyncio.run(cap.start())
    frame = asyncio.run(cap.grab_frame())
    assert frame.dtype == np.uint8
    assert len(frame.shape) == 3
    assert frame.shape[2] == 3   # BGR, no alpha

def test_mss_capture_resolution_consistent(xvfb, monkeypatch):
    monkeypatch.setenv('DISPLAY', xvfb)
    cap = MssCapture(monitor=1)
    asyncio.run(cap.start())
    frame = asyncio.run(cap.grab_frame())
    w, h = cap.resolution
    assert frame.shape == (h, w, 3)

def test_mss_capture_no_memory_leak(xvfb, monkeypatch):
    import psutil, os
    monkeypatch.setenv('DISPLAY', xvfb)
    cap = MssCapture(monitor=1)
    asyncio.run(cap.start())
    
    proc = psutil.Process(os.getpid())
    mem_before = proc.memory_info().rss
    for _ in range(50):
        asyncio.run(cap.grab_frame())
    mem_after = proc.memory_info().rss
    
    delta_mb = (mem_after - mem_before) / 1024 / 1024
    assert delta_mb < 50, f"Memory grew by {delta_mb:.1f}MB"
