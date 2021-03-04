from flask import Response, stream_with_context
import concurrent.futures
import time
import re
import os


def send_until_end_of_request(app, func, args=(), on_end=lambda ret_func: None):
    def thread():
        with app.app_context(), app.test_request_context():
            return func(*args)

    def exec():
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(thread)

        while not future.done():
            yield b""
            time.sleep(1)
        ret = future.result()
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

def fix_tag_path(tag_path: list) -> list:
    if tag_path is None:
        return []

    tag_path_dict = {tag['id']: tag for tag in tag_path}
    new_tag_path = []

    def try_append(tag):
        parent = tag['parent']
        if parent == 0 or parent == new_tag_path[-1]['id']:
            new_tag_path.append({'id': tag['id'], 'name': tag['name']})
            tag_path.remove(tag)
            return
        try_append(tag_path_dict[parent])
        try_append(tag)

    while tag_path:
        for tag in tag_path:
            try_append(tag)
    
    return new_tag_path