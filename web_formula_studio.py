from __future__ import annotations

import socket
import threading
import time
import webbrowser

from web_formula_backend import create_app


def find_available_port(start: int = 5173, attempts: int = 100) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("未找到可用的本地端口")


def main() -> int:
    port = find_available_port()
    app = create_app()
    url = f"http://127.0.0.1:{port}/"

    server = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    server.start()
    time.sleep(0.8)
    webbrowser.open(url)

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
