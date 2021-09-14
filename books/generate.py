import json
import re
import time

import requests
from bs4 import BeautifulSoup
from requests_file import FileAdapter


VERSION_RE = re.compile(r"^\s*Version (?P<version>.+)\s*$")

source_url = input("URL of the book (NOCHUNKS version, find them "
                   "here: https://www.linuxfromscratch.org/lfs/downloads/\n> ")

START = time.time()
config = {
    "version": 2.1,
    "edition": "",
    "book": source_url,
    "chapters": {}
}
session = requests.Session()
session.mount('file://', FileAdapter())

print("Getting the source... ", end="\r")
with session.get(source_url, stream=True) as resp:
    response = b""
    for chunk in resp.iter_content(8196):
        response += chunk
        print(f"Getting the source... {len(response)}", end="\r")
resp.raise_for_status()
print(f"Getting the source... {len(response)} OK")

print("Parsing the contents... ", end="")
soup = BeautifulSoup(response, 'html.parser')
print(f"OK, {len(soup.find_all())} tags")

print("Getting book edition... ", end="")
edition_r = soup.find(string=VERSION_RE)
edition = VERSION_RE.match(edition_r).group('version')
config['edition'] = edition
print(edition)

print("Getting Table of Contents... ", end="")
toc = soup.find(class_="toc")
print(f'{len(toc.find_all(class_="part"))} parts', end=", ")
print(f'{len(toc.find_all(class_="chapter"))} chapters', end=", ")
print(f'{len(toc.find_all(class_="sect1"))} sections')

print("Finding ToC items... ", end="")
toc_items: list = toc.ul.find_all('li', recursive=False)
print(f"found {len(toc_items)} items.")

# Preprocessing: first preface
print("Preprocessing items... ")
wrapping = soup.new_tag('li')
wrapping['class'] = 'part'
wrapping.append(soup.new_tag('h3'))
wrapping.h3.string = "0. Preface"
wrapping.append(soup.new_tag('ul'))
# get preface
preface = toc_items[0]  # this should always be true
preface['class'] = "chapter"
preface.h4.string = "0. Preface"
# new_preface = preface.wrap(wrapping.ul)
wrapping.ul.append(preface)
print('\t1. Replaced Preface object')

toc_items[0] = wrapping  # i am tired and i still have no idea how the wrap method works. it's been 3 hours.
toc_items.remove([item for item in toc_items if item['class'][0] == 'index'][0])  # extremely hacky
print('\t2. Removed index')

for item in toc_items:
    item.h3.string = item.h3.string.strip()
print('\t3. Stripped some whitespaces')

print('Current ToC:')
for i in toc_items:
    print(i.h3.string)

statistics = [0, 0, 0]

print("Building full ToC... ")
for part_c, i in enumerate(toc_items):
    print(f'Found part {i.h3.string}')
    statistics[0] += 1
    config_item = {
        'index': part_c,
        'chapters': {}
    }
    for chapter_c, chapter in enumerate(i.ul.find_all('li', class_=['chapter', 'preface'], recursive=False)):
        chapter.h4.string = ' '.join(chapter.h4.string.split())
        print(f'Found chapter {chapter.h4.string}')
        statistics[1] += 1
        config_chapter = {
            'index': chapter_c + 1,
            'sections': {}
        }
        for section_c, section in enumerate(chapter.ul.find_all('li', class_='sect1', recursive=False)):
            section.a.string = ' '.join(section.a.string.split())
            # config_section = {
            #     'index': section_c + 1,
            #     'name': section.a.string
            # }
            print(f'Found section {section.a.string}')
            statistics[2] += 1
            config_chapter['sections'][section.a.string] = section.a['href']  # config_section

        desc_l = chapter.h4.string.split('.')
        if len(desc_l) <= 1:
            desc = desc_l[0]
        else:
            desc = desc_l[1]
        config_item['chapters'][desc.strip()] = config_chapter

    config['chapters'][i.h3.string.split('. ')[1]] = config_item

print("Saving ToC json... ")
with open(f'{edition}.json', 'w+') as file:
    json.dump(config, file, indent=4)

print(
    '======================================\n' +
    '|             Statistics             |\n' +
    '|------------------------------------|\n' +
    '| Parts: ' + f'{statistics[0]}'.rjust(27) + ' |\n' +
    '| Chapters: ' + f'{statistics[1]}'.rjust(24) + ' |\n' +
    '| Sections: ' + f'{statistics[2]}'.rjust(24) + ' |\n' +
    '|------------------------------------|\n' +
    '| Elapsed Time: ' + f'{round(time.time()*1000-START*1000, 2)}ms'.rjust(20) + ' |\n' +
    '======================================\n'
)
print(f'Configuration is saved to {edition}.json')
