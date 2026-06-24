"""
Render.com uchun keep-alive server.
Render free tier botni uyquga qo'ymasligi uchun HTTP server qo'shamiz.
"""
import asyncio
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", 10000))


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti OK")

    def log_message(self, format, *args):
        pass  # Log chiqmaslik uchun


def run_http_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info(f"Health check server port {PORT} da ishga tushdi")
    server.serve_forever()


def start_keep_alive():
    thread = threading.Thread(target=run_http_server, daemon=True)
    thread.start()
