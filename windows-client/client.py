#!/usr/bin/env python3
import argparse
import socket
import logging
import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    parser = argparse.ArgumentParser(description='ThunderKVM Client (Windows)')
    parser.add_argument('--host',     default='192.168.100.2', help='Ubuntu server IP')
    parser.add_argument('--port',     type=int, default=7777)
    parser.add_argument('--fullscreen', action='store_true')
    parser.add_argument('--log-level', default='INFO')
    args = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    logger = logging.getLogger('thunder-client')
    
    logger.info(f"Connecting to Ubuntu at {args.host}:{args.port}...")
    
    # Connect TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    try:
        sock.connect((args.host, args.port))
    except ConnectionRefusedError:
        print(f"ERROR: Cannot connect to {args.host}:{args.port}")
        print("Make sure the Ubuntu server is running: python server.py")
        sys.exit(1)
    
    logger.info("Connected!")
    
    from src.net.client import ThunderClient
    client = ThunderClient(sock, fullscreen=args.fullscreen)
    client.run()

if __name__ == '__main__':
    main()
