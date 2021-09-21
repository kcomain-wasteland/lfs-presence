import helpers


async def select_section(chapter, current):
    if 'sections' not in chapter:
        chapter['sections'] = ()
    if len(chapter['sections']):
        print('[i] Chapter ')


async def select_things(book: dict, current):
    sel_part = await helpers.select("Select part: ", choices=book['chapters'])
    if sel_part is None:
        return
    elif len(book['chapters'][sel_part]['chapters']) == 0:
        print(f'[i] Part {sel_part} doesn\'t have any chapters.')
        return

    sel_chapter = await helpers.select("Select chapter: ", choices=book['chapters'][sel_part]['chapters'])
    if sel_chapter is None:
        return

    sel_section = await helpers.select(
        "Select section: ",
        choices=book['chapters'][sel_part]['chapters'][sel_chapter]['sections']
    )
    if sel_section is None:
        return

    current.part = book['chapters'][sel_part]['index']
    current.part_title = sel_part
    current.chapter = book['chapters'][sel_part]['chapters'][sel_chapter]['index']
    current.chapter_title = sel_chapter
    current.section = sel_section
