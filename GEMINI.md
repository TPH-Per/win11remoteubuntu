# ThunderKVM AI Context

## Project Overview
ThunderKVM is a software KVM switch over a direct Thunderbolt/USB-C cable connecting two laptops.
- **Laptop A (Windows):** Runs the client (`windows-client/`). Captures inputs, decodes H.264 video, and renders the remote screen.
- **Laptop B (Ubuntu):** Runs the server (`ubuntu-server/`). Captures the screen, encodes to H.264, executes received inputs.

## Build and Run Commands
- **Windows Client:** `cd windows-client` -> `python client.py --host 192.168.100.2`
- **Ubuntu Server:** `cd ubuntu-server` -> `python server.py`
- **Run Tests:** Use `pytest` on `tests/`, `ubuntu-server/tests/`, or `windows-client/tests/`. Ensure `PYTHONPATH="."` is set.

## Code Style
- Use Python 3.11+ syntax.
- Use `pydantic` for serialization models (events).
- Use `struct` for binary framing protocol.
- Follow existing dependency bounds (`pynput`, `pygame-ce`, `av`, `mss`).

## Security & Architecture Constraints
- **No internet required.** Must function purely offline over raw TCP.
- Do not introduce WebRTC or external relay dependencies.
- Minimize input and video latency (target < 30ms pipeline).
