#!/usr/bin/env python3
import argparse
import logging
import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    parser = argparse.ArgumentParser(description='ThunderKVM Server (Ubuntu)')
    parser.add_argument('--host',     default='0.0.0.0',    help='Bind address')
    parser.add_argument('--port',     type=int, default=7777, help='TCP port')
    parser.add_argument('--fps',      type=int, default=60,  help='Target FPS')
    parser.add_argument('--bitrate',  type=int, default=4000, help='H.264 bitrate kbps')
    parser.add_argument('--encoder',  default='software', choices=['software', 'vaapi'])
    parser.add_argument('--monitor',  type=int, default=1,   help='Monitor index (1=primary)')
    parser.add_argument('--log-level',default='INFO')
    args = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    
    wayland = os.environ.get('WAYLAND_DISPLAY')
    xdg = os.environ.get('XDG_SESSION_TYPE', '')
    if wayland or xdg.lower() == 'wayland':
        print("WARNING: Wayland detected. mss requires X11.")
        print("Fix: Log out → chọn 'Ubuntu on Xorg' ở màn hình đăng nhập")
        print("  OR run: export DISPLAY=:0 GDK_BACKEND=x11 XDG_SESSION_TYPE=x11")
        print("  OR force X11 session permanently:")
        print("     sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/' /etc/gdm3/custom.conf")
        sys.exit(1)
        
    if not os.environ.get('DISPLAY') and sys.platform != 'win32':
        print("ERROR: DISPLAY environment variable not set.")
        print("Run: export DISPLAY=:0")
        sys.exit(1)
    
    from src.net.server import ThunderServer
    server = ThunderServer(
        host=args.host, port=args.port,
        fps=args.fps, bitrate_kbps=args.bitrate,
    )
    
    print(f"[ThunderKVM] Server ready on {args.host}:{args.port}")
    print(f"[ThunderKVM] Connect from Windows: python client.py --host 192.168.100.2")
    
    server.serve_forever()

if __name__ == '__main__':
    main()
