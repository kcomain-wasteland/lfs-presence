import json
import os
import hashlib

from cache import get_cache


def get_configs():
    candidates = [i for i in os.listdir('books') if i.endswith('.json')]
    available = {}
    for candidate in candidates:
        with open(os.path.join('books', candidate)) as f:
            try:
                conf = json.load(f)
            except json.JSONDecodeError:
                continue

        if 'version' not in conf:
            continue
        if conf['version'] > 1 or conf['version'] < 1:
            continue
        print(f'[+] found config {conf["edition"]}')

        available[conf['edition']] = candidate
    return available


def load_config(config):
    print('[+] checking if config exists... ', end='')
    filepath = os.path.join('books', config)
    if not os.path.exists(filepath):
        print('no')
        print(f'[!] book config {config} doesn\'t exist')
        hash_ = None
    else:
        print('yes')
        print('[+] calculating checksum... ', end='')
        with open(filepath, 'rb') as f:
            hash_ = hashlib.sha512(f.read()).hexdigest()
        print(hash_[0:25] + '...')

    print('[+] checking if cache of this config exists... ')
    book = get_cache(config, hash_)

    if book is None and filepath is None:
        raise FileNotFoundError("Cannot find configuration file")
    if book:
        return book

    print('[+] that\'s fine, compiling it now')
    with open(filepath) as f:
        book_raw = json.load(f)

    book = {
        'checksum': hash_,
        'metadata': {
            'edition': book_raw['edition'],
            'config_version': book_raw['version'],
            'book_url': book_raw['book']
        },
        'index': {},
        'sections': []  # flattened list
    }
    print('[+] template created')

    # This is like restructuring the json while i could've done this with the generator instead
    # Unnecessarily complicated code with sophie

