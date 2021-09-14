import asyncio
import os

import questionary
from dotenv import load_dotenv
from pypresence import AioPresence, InvalidID

from loader import get_configs, load_config

print('[i] loading...')
load_dotenv(verbose=True)


class CurrentProgress:
    part: int = 0
    part_title: str = ''
    chapter: int = 0
    chapter_title: str = ''
    section: str = ''

    def __init__(self, part=0, chapter=0, section=''):
        self.part = part
        self.chapter = chapter
        self.section = section

    def __repr__(self):
        return f"<CurrentProgress object at {hex(id(self))} " \
               f"part={self.part} " \
               f"chapter={self.chapter} " \
               f"section={self.section}>"

    def __str__(self):
        return f"Chapter {self.part}.{self.chapter}: {self.section}"


async def backoff(coro, max_delay=60, step=2, max_retries=0, catch_errors=(Exception,)):
    delay = 0
    retries = 0
    success = False
    while not success:
        try:
            await coro()
        except catch_errors as e:
            retries += 1
            print(f'[!] coroutine errored - {type(e).__name__}: {e} \n'
                  f'[!] attempt {retries} out of {max_retries}, retrying in {delay} seconds...')
            if retries >= max_retries != 0:
                print(f'[x] max retries ({max_retries} reached, not attempting again.')
                raise e
            await asyncio.sleep(delay)
            if (delay + step) <= max_delay:
                delay += step
            elif (delay + step) > max_delay:
                delay = max_delay
        else:
            break


async def update_presence(presence, **kwargs):
    if 'large_image' not in kwargs:
        kwargs['large_image'] = 'tux'
    try:
        await presence.update(**kwargs)
    except InvalidID:  # broken pipe is broken pipe not this thing..
        await presence.connect()
        await presence.update(**kwargs)


async def main():
    presence = AioPresence(client_id=os.environ.get("CLIENT_ID"), loop=asyncio.get_running_loop())
    print('[i] connecting to discord... ', end='')
    await backoff(presence.connect, catch_errors=(ConnectionRefusedError,))
    print('connected.')

    print('[i] getting configurations...')
    configs = get_configs()
    configs['Create new'] = ''
    selected = await questionary.select("Choose a book:", choices=configs, qmark="[?]") \
        .ask_async(kbi_msg="[!] cancelled")
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
    current = CurrentProgress(0, 0, '')

    async def select_things():
        sel_part = await questionary.select(
            "Select part: ",
            choices=book['chapters'],
            qmark="[?]").ask_async(kbi_msg="[!] cancelled")
        if sel_part is None:
            return
        elif len(book['chapters'][sel_part]['chapters']) == 0:
            print(f'[i] Part {sel_part} doesn\'t have any chapters.')
            return

        sel_chapter = await questionary.select(
            "Select chapter: ",
            choices=book['chapters'][sel_part]['chapters'],
            qmark="[?]").ask_async(kbi_msg="[!] cancelled")
        if sel_chapter is None:
            return

        sel_section = await questionary.select(
            "Select section: ",
            choices=book['chapters'][sel_part]['chapters'][sel_chapter]['sections'],
            qmark="[?]").ask_async(kbi_msg="[!] cancelled")
        if sel_section is None:
            return

        current.part = book['chapters'][sel_part]['index']
        current.part_title = sel_part
        current.chapter = book['chapters'][sel_part]['chapters'][sel_chapter]['index']
        current.chapter_title = sel_chapter
        current.section = sel_section

    await select_things()

    while True:
        print(f'[i] Current progress: {current}')
        break


if __name__ == '__main__':
    asyncio.run(main())
