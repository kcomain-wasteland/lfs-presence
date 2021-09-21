import asyncio
import os

from dotenv import load_dotenv
from pypresence import AioPresence

import helpers
import questions
from loader import get_configs, load_config

print('[i] loading...')
load_dotenv(verbose=True)


async def main():
    presence = AioPresence(client_id=os.environ.get("CLIENT_ID"), loop=asyncio.get_running_loop())
    print('[i] connecting to discord... ', end='')
    await helpers.backoff(presence.connect, catch_errors=(ConnectionRefusedError,))
    print('connected.')

    print('[i] getting configurations...')
    configs = get_configs()
    configs['Create new'] = ''
    selected = await helpers.select("Choose a book:", choices=configs)
    if selected is None:
        return

    print('[i] loading config...')
    if selected.lower() == "create new":
        print('[i] To generate configuration for a book, cd to the books directory and run `python generate.py`')
        return

    # Load the config
    book = load_config(configs[selected])
    del configs

    print(f'[i] Config version {book["version"]}, Book v{book["edition"]}')
    current = helpers.CurrentProgress()

    await questions.select_things(book, current)

    while True:
        print(f'[i] Current progress: {current}')
        break


if __name__ == '__main__':
    asyncio.run(main())
