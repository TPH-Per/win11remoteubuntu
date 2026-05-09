import yaml
import os

def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        # Fallback to defaults
        return {
            "network": {"ubuntu_ip": "192.168.100.2", "windows_ip": "192.168.100.1", "port": 7777},
            "server": {"monitor": 1, "fps": 60, "bitrate_kbps": 4000, "encoder": "auto", "display": ":0"},
            "client": {"fullscreen": False, "decoder": "software", "show_overlay": True, "overlay_position": "top-left"},
            "kvm": {"toggle_hotkey": "scroll_lock", "cursor_mode": "relative", "show_state_indicator": True},
            "performance": {"tcp_send_buffer": 262144, "tcp_recv_buffer": 262144, "frame_queue_size": 2, "input_rate_limit_hz": 60, "keyframe_interval_s": 4}
        }
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
