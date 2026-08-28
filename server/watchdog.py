#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VideoForgeSuite 守护进程：每 30s 检查 8765 端口，死了自动拉起 orchestrator"""
import socket, subprocess, sys, time, os

PY = sys.executable or "python"
ORCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orchestrator.py")
PORT = 8765
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "watchdog.log")

def port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        try:
            s.connect(("127.0.0.1", port))
            return True
        except OSError:
            return False

def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def main():
    log("watchdog started")
    while True:
        try:
            if not port_open(PORT):
                log("server down, restarting...")
                subprocess.Popen([PY, ORCH],
                                 creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0)
                time.sleep(5)
        except Exception as e:
            log(f"watchdog error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    main()
