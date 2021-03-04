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

def create_drive_path(all_files, root, drive_path_key):
    parents_map = {}
    
    for file in all_files:
        if not 'parents' in file:
            continue
        parent = file['parents'][0]
        if not parent in parents_map:
            parents_map[parent] = []
        parents_map[parent].append(file)
    
    files_dict = {}
    def build_path(folder, path):
        children = parents_map[folder['id']]
        for child in children:
            if not 'folder' in child['mimeType']:
                child[drive_path_key] = path
                files_dict[child['id']] = child
            else:
                new_path = list(path)
                new_path.append({'id': child['id'], 'name': child['name']})
                build_path(child, new_path)
    build_path(root, [{'id': root['id'], 'name': root['name']}])

    return files_dict

def fix_tag_path(tags_path: list) -> list:
    if tags_path is None:
        return [[]]

    tag_path_dict = {tag['id']: tag for tag in tags_path}

    for tag in tags_path:
        parent_id = tag['parent']
        parent_tag = tag_path_dict[parent_id] if parent_id else None
        
        tag['parent_tag'] = parent_tag
        if parent_tag:
            parent_tag['is_parent'] = True

    leaf_tags = list(tags_path)
    
    for tag in tags_path:
        if 'is_parent' in tag:
            leaf_tags.remove(tag)

    new_tags_path = [[]] * len(leaf_tags)

    for i in range(len(leaf_tags)):
        current_tag = leaf_tags[i]
        tag_path = []

        while current_tag:
            tag_path.append({'id': current_tag['id'], 'name': current_tag['name']})
            current_tag = current_tag['parent_tag']

        tag_path.reverse()
        new_tags_path[i] = tag_path

    return new_tags_path