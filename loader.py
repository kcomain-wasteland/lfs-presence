import json
import os


def get_configs():
    candidates = [i for i in os.listdir('books') if i.endswith('.json')]
    available = {}
    supported_versions = (2.1,)
    for candidate in candidates:
        with open(os.path.join('books', candidate)) as f:
            try:
                conf = json.load(f)
            except json.JSONDecodeError:
                continue

        if 'version' not in conf:
            continue
        if conf['version'] not in supported_versions:
            continue
        print(f'[+] found config {conf["edition"]}')

        available[conf['edition']] = candidate
    return available


def load_config(config):
    print('[+] checking if config exists... ', end='')
    filepath = os.path.join('books', config)
    if not os.path.exists(filepath):
        print('no')
        raise FileNotFoundError(f'book config {config} doesn\'t exist')
    else:
        print('yes')

    with open(filepath) as f:
        book = json.load(f)

    print('[+] config loaded.')
    return book
