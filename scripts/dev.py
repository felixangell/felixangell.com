#!/usr/bin/env python3
"""Local preview with rebuilds and browser reloads; standard library only."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from threading import Event, Thread
from urllib.parse import urlsplit
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
revision = str(time.time_ns())
stopped = Event()
RELOAD = b"""<script>
(() => {
  let version;
  async function poll() {
    try {
      const response = await fetch('/__dev_version', {cache: 'no-store'});
      if (response.ok) {
        const next = await response.text();
        if (version !== undefined && version !== next) location.reload();
        version = next;
      }
    } catch (_) {}
    setTimeout(poll, 500);
  }
  poll();
})();
</script>
"""


def snapshot():
    files = {}
    for directory, folders, names in os.walk(ROOT):
        folders[:] = [name for name in folders if not name.startswith('.')
                      and name != '__pycache__']
        for name in names:
            path = Path(directory) / name
            if name.startswith('.') or (path.suffix == '.html'
                                         and not path.is_relative_to(ROOT / 'templates')):
                continue
            try:
                stat = path.stat()
                files[path] = (stat.st_mtime_ns, stat.st_size)
            except FileNotFoundError:
                pass  # An editor may replace a file while we scan.
    return files


def rebuild():
    return subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build.py')],
                          cwd=ROOT).returncode == 0


def watch(previous):
    global revision
    while not stopped.wait(0.5):
        current = snapshot()
        if current != previous:
            previous = current
            if rebuild():
                revision = str(time.time_ns())
            else:
                print('Fix the build error and save to retry.', flush=True)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def send_head(self):
        if urlsplit(self.path).path == '/__dev_version':
            data = revision.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            return BytesIO(data)

        path = Path(self.translate_path(self.path))
        if path.is_dir() and urlsplit(self.path).path.endswith('/'):
            path = path / 'index.html'
        if path.is_file() and path.suffix == '.html':
            data = path.read_bytes()
            data = data.replace(b'</body>', RELOAD + b'</body>') if b'</body>' in data else data + RELOAD
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            return BytesIO(data)
        return super().send_head()


if __name__ == '__main__':
    previous = snapshot()
    if not rebuild():
        sys.exit(1)
    with ThreadingHTTPServer(('127.0.0.1', 8000), Handler) as server:
        watcher = Thread(target=watch, args=(previous,), daemon=True)
        watcher.start()
        print('Live preview: http://localhost:8000 (Ctrl-C to stop)', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            stopped.set()
            watcher.join()
