from flask import Response, stream_with_context
import concurrent.futures
import time
import re
import os


def sendUntilEndOfRequest(app, func, args=(), on_end=lambda ret_func: None):
    ret = None

    def thread():
        nonlocal ret
        with app.app_context(), app.test_request_context():
            ret = func(*args)

    def exec():
        nonlocal ret
        executor = concurrent.futures.ThreadPoolExecutor()

        future = executor.submit(thread)

        while not ret:
            yield b""
            time.sleep(1)
        on_end(ret)
        yield ret

    return Response(stream_with_context(exec()))


def path_to(root, path):
    root = os.path.abspath(os.path.dirname(root))
    return os.path.join(root, path)


_nsre = re.compile('([0-9]+)')


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s.get('name'))]


class ChunkHolder(object):
    def __init__(self):
        self.chunk = None

    def write(self, chunk):
        """Save current chunk"""
        self.chunk = chunk
