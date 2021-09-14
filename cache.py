import lzma
import os
import pickle
import typing


def _remove_file(filepath):
    print('[~] removing cache file... ', end='')
    try:
        os.remove(filepath)
    except PermissionError:
        print('failed: permission denied')
    else:
        print('ok')


def get_cache(config, sha_512_hash=None) -> typing.Optional[dict]:
    filepath = os.path.join('cache', config + '.xz')
    if not os.path.exists(filepath):
        print(f'[~] cache miss: missing cache file ({config})')
        return None
    print('[~] loading cache file... ', end='')
    try:
        with lzma.open(filepath) as f:
            cache = pickle.load(f)
    except (pickle.UnpicklingError, EOFError, lzma.LZMAError, PermissionError) as e:
        print(f'unable to load file: {type(e).__name__}')
        print(f'[~] cache miss: possibly corrupted cache file ({config})')

        _remove_file(filepath)
        return None
    print('ok')

    print('[~] verifying checksum... ', end='')
    if sha_512_hash and 'checksum' in cache:
        if not cache['checksum']:
            print('skipped: cache doesn\'t have a valid checksum field')
        elif sha_512_hash != cache['checksum']:
            print('failed')
            print(f'[~] cache miss: non-matching checksums - either the config changed or cache is outdated ({config})')
            _remove_file(filepath)
            return None
        else:
            print('passed')
    else:
        print('skipped')

    print(f'[i] cache hit: ({config})')
    return cache
