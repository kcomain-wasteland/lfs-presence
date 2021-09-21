import asyncio

import questionary
from pypresence import InvalidID


class CurrentProgress:
    part: int = 0
    part_title: str = 'unknown'
    chapter: int = 0
    chapter_title: str = 'unknown'
    section: str = 'unknown'

    def __init__(self, part=None, chapter=None, section=None):
        if part:
            self.part = part
        if chapter:
            self.chapter = chapter
        if section:
            self.section = section

    def __repr__(self):
        return f"<CurrentProgress object at {hex(id(self))} " \
               f"part={self.part} " \
               f"chapter={self.chapter} " \
               f"section={self.section}>"

    def __str__(self):
        return f"Chapter {self.part}.{self.chapter}: {self.section}"


def generate_choices(choices: list):
    return_list = []
    for i in choices:
        if i == '--sep':
            return_list.append(questionary.Separator())
            continue
        return_list.append(questionary.Choice.build(i))

    return return_list


async def select(*args, **kwargs):
    if 'qmark' not in kwargs:
        kwargs['qmark'] = '[?]'
    if 'pointer' not in kwargs:
        kwargs['pointer'] = '-->'
    ask_q = questionary.select(*args, **kwargs)
    return await ask_q.ask_async(kbi_msg="[!] cancelled.")


async def update_presence(presence, **kwargs):
    if 'large_image' not in kwargs:
        kwargs['large_image'] = 'tux'
    try:
        await presence.update(**kwargs)
    except InvalidID:  # broken pipe is broken pipe not this thing..
        await presence.connect()
        await presence.update(**kwargs)


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
