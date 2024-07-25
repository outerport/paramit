from collections import deque
import os
import requests
import base64

SERVER_URL = 'http://127.0.0.1:8000/job'

def load_directory(directory: str):
    code_dir = {}
    q = deque([(code_dir, directory)])
    while len(q) > 0:
        node, dir = q.popleft()
        rel_dir = os.path.relpath(dir, directory)
        for obj in os.listdir(dir):
            full_path = os.path.join(dir, obj)
            rel_path = os.path.join(rel_dir, obj)
            if os.path.isdir(full_path):
                node[rel_path] = {}
                q.append((node[rel_path], full_path))
            else:
                content_bytes = open(full_path, 'rb').read()
                encoded = base64.b64encode(content_bytes).decode('utf-8')
                node[rel_path] = encoded
    return code_dir

def run_code_on_cloud(script_path, cli_args):
    directory = os.path.dirname(script_path)

    code_dir = load_directory(directory)
    data = {
        'code_dir': code_dir,
        'script_path': script_path,
        'cli_args': cli_args
    }
    print(f'Running on the cloud at {SERVER_URL}')
    with requests.post(SERVER_URL, json=data, stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                print(chunk.decode('utf-8'))