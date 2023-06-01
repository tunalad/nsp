#!/usr/bin/env python
# pylint: disable=consider-using-sys-exit
# biblegateway.com scrapper (best out there afaik), main logic in main()

import re
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from srtools import cyrillic_to_latin as to_lat, latin_to_cyrillic as to_cyr

def get_soup(url):# {{{
    # main soup
    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    return soup# }}}

def get_passasge(passage, bible_version = "niv"):# {{{
    # verses soup
    base_url= "https://www.biblegateway.com"

    soup = get_soup(f"{base_url}/passage/?search={passage}&version={bible_version}")
    container = soup.find_all("div", class_="passage-content passage-class-0")[0]
    subcontainer = container.contents[0]
    return subcontainer# }}}

def get_verse(passage):# {{{
    # get a single verse
    for item in passage.find_all(class_=["versenum", "chapternum", "footnote" , "full-chap-link"]):
        item.decompose()

    for item in passage.find_all("h3"):
        item.decompose()


    verse = passage.get_text().strip()
    verse = " ".join(verse.split())
    verse = re.sub(r'([,.!?;:])\s*', r'\1 ', verse)  # Add space after punctuation marks
    verse = verse.rstrip()  # Remove extra whitespace at the end
    verse = verse.replace(" “", "“")  # Remove whitespace before closing quotation mark
    verse = verse.replace(" ’", "’")  # Remove whitespace before closing singe quotation mark
    return verse# }}}

def get_verses(passage):# {{{
    # get multiple verses (per chapter)
    # removes extra stuff
    [item.decompose() for item in passage.find_all(class_=["chapternum", "footnote", "footnotes", "full-chap-link"])]
    [item.decompose() for item in passage.find_all(["h2", "h3", "h4"])]

    # finds versenum items, we use those to split stuff up
    verses = []
    for v in passage.find_all(class_=["versenum"]):
        verses.append(v.get_text(strip=True))

    # we fix the string a little
    passage_string = passage.get_text().replace('\xa0', ' ').replace('\n', ' ').strip()
    passage_string = re.sub(r'(\D)(\d+)(\D)', r'\1 \2 \3', passage_string)

    # safer character for splitting verses with
    for v in verses:
        if (" " + v + " ") in passage_string:
            passage_string = passage_string.replace((" " + v + " "), "¤")
            continue

    # split it up
    passage_string = fix_text(passage_string)
    split_passage = passage_string.split("¤")

    return list(map(fix_text, split_passage))# }}}

def get_books_list(version):# {{{
    # returns a list of books with chapters count
    base_url= "https://www.biblegateway.com/versions"

    soup = get_soup(f"{base_url}/{version}")
    container = soup.find_all("table", class_="infotable chapterlinks updatepref")[0]
    books_soup = container.find_all("tr")

    books = []

    for book in books_soup:
        chapters = (book.find("td", class_="book-name").find("span", class_="num-chapters").text.strip())
        for item in book.find("td", class_="book-name").find_all("span"):
            item.extract()
        book_name = book.find('td', class_='book-name').text.strip()

        books.append({ "name": book_name, "chapters": int(chapters) })

    return books# }}}

def get_short_name(book_name):# {{{
    # shorthands for books
    book_map = {
        # english books (kjv)
        'Genesis': 'Ge',
        'Exodus': 'Exo',
        'Leviticus': 'Lev',
        'Numbers': 'Num',
        'Deuteronomy': 'Deu',
        'Joshua': 'Josh',
        'Judges': 'Jdgs',
        'Ruth': 'Ruth',
        '1 Samuel': '1Sm',
        '2 Samuel': '2Sm',
        '1 Kings': '1Ki',
        '2 Kings': '2Ki',
        '1 Chronicles': '1Chr',
        '2 Chronicles': '2Chr',
        'Ezra': 'Ezra',
        'Nehemiah': 'Neh',
        'Esther': 'Est',
        'Job': 'Job',
        'Psalms': 'Psa',
        'Psalm': 'Psa',
        'Proverbs': 'Prv',
        'Ecclesiastes': 'Eccl',
        'Song of Solomon': 'SSol',
        'Isaiah': 'Isa',
        'Jeremiah': 'Jer',
        'Lamentations': 'Lam',
        'Ezekiel': 'Eze',
        'Daniel': 'Dan',
        'Hosea': 'Hos',
        'Joel': 'Joel',
        'Amos': 'Amos',
        'Obadiah': 'Obad',
        'Jonah': 'Jonah',
        'Micah': 'Mic',
        'Nahum': 'Nahum',
        'Habakkuk': 'Hab',
        'Zephaniah': 'Zep',
        'Haggai': 'Hag',
        'Zechariah': 'Zec',
        'Malachi': 'Mal',
        'Matthew': 'Mat',
        'Mark': 'Mark',
        'Luke': 'Luke',
        'John': 'John',
        'Acts': 'Acts',
        'The Acts': 'Acts',
        'Romans': 'Rom',
        '1 Corinthians': '1Cor',
        '2 Corinthians': '2Cor',
        'Galatians': 'Gal',
        'Ephesians': 'Eph',
        'Philippians': 'Phi',
        'Colossians': 'Col',
        '1 Thessalonians': '1Th',
        '2 Thessalonians': '2Th',
        '1 Timothy': '1Tim',
        '2 Timothy': '2Tim',
        'Titus': 'Titus',
        'Philemon': 'Phmn',
        'Hebrews': 'Heb',
        'James': 'Jas',
        '1 Peter': '1Pet',
        '2 Peter': '2Pet',
        '1 John': '1Jn',
        '2 John': '2Jn',
        '3 John': '3Jn',
        'Jude': 'Jude',
        'Revelation': 'Rev',
        # serbian books (nsp)
        '1 Mojsijeva': '1Mo',
        '2 Mojsijeva': '2Mo',
        '3 Mojsijeva': '3Mo',
        '4 Mojsijeva': '4Mo',
        '5 Mojsijeva': '5Mo',
        'Knjiga Isusa Navina': 'JNav',
        'Knjiga o sudijama': 'Sud',
        'Knjiga o Ruti': 'Rut',
        '1 Knjiga Samuilova': '1Sam',
        '2 Knjiga Samuilova': '2Sam',
        '1 Knjiga o carevima': '1Car',
        '2 Knjiga o carevima': '2Car',
        '1 Knjiga dnevnika': '1Dne',
        '2 Knjiga dnevnika': '2Dne',
        'Jezdrina': 'Jez',
        'Knjiga Nemijina': 'Nem',
        'Knjiga o Jestiri': 'Jest',
        'Knjiga o Jovu': 'Jov',
        'Psalmi': 'Psm',
        'Priče Solomonove': 'Prc',
        'Knjiga propovednikova': 'Prop',
        'Pesma nad pesmama': 'PnP',
        'Knjiga proroka Isaije': 'Isa',
        'Knjiga proroka Jeremije': 'Jer',
        'Plač Jeremijin': 'PlaJer',
        'Knjiga proroka Jezekilja': 'Eze',
        'Knjiga proroka Danila': 'Dan',
        'Knjiga proroka Osije': 'Osi',
        'Knjiga proroka Joila': 'Joel',
        'Knjiga proroka Amosa': 'Amos',
        'Knjiga proroka Avdije': 'Avd',
        'Knjiga proroka Jone': 'Jon',
        'Knjiga proroka Miheja': 'Mih',
        'Knjiga proroka Nauma': 'Nah',
        'Knjiga proroka Avakuma': 'Avk',
        'Knjiga proroka Sofonije': 'Sof',
        'Knjiga proroka Ageja': 'Ag',
        'Knjiga proroka Zaharije': 'Zah',
        'Knjiga proroka Malahije': 'Mal',
        'Matej': 'Mat',
        'Marko': 'Mark',
        'Luka': 'Luk',
        'Jovan': 'Joh',
        'Dela apostolska': 'Dap',
        'Rimljanima': 'Rom',
        '1 Korinćanima': '1Kor',
        '2 Korinćanima': '2Kor',
        'Galatima': 'Gal',
        'Efescima': 'Efe',
        'Filipljanima': 'Fil',
        'Kološanima': 'Kol',
        '1 Solunjanima': '1Sol',
        '2 Solunjanima': '2Sol',
        '1 Timoteju': '1Tim',
        '2 Timoteju': '2Tim',
        'Titu': 'Tit',
        'Filimonu': 'Fil',
        'Jevrejima': 'Heb',
        'Jakovljeva': 'Jak',
        '1 Petrova': '1Pet',
        '2 Petrova': '2Pet',
        '1 Jovanova': '1Jov',
        '2 Jovanova': '2Jov',
        '3 Jovanova': '3Jov',
        'Judina': 'Jud',
        'Otkrivenje': 'Otk',
    }
    
    return book_map.get(book_name, 'Unknown')# }}}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def fix_text(text):# {{{
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text# }}}

def append_file(file_path, text):# {{{
    with open(file_path, "a+") as file:
        file.write(text + "\n")# }}}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def main():
    bible_version = "NSP" #"ERV-SR"
    TSV_FILE = "nsp.tsv"
    books = get_books_list("King-James-Version-KJV-Bible") # value from biblegateway.com/versions/...
    #books = get_books_list("New-Serbian-Translation-NSP-Bible")

    # iterates through all the books and chapters, exports them in tsv
    for book in books:
        book_index = books.index(book)+1
        for ch in range(int(book["chapters"])):
            book_chapter = f"{book['name']} {ch+1}"

            passage = get_passasge(book_chapter, bible_version)
            verses = get_verses(passage)
            for v in verses:
                verse_index = verses.index(v)+1
                # tsv file format
                line = (to_lat(book["name"]) +
                    "\t" + 
                    get_short_name(to_lat(book["name"])) +
                    "\t" + 
                    str(book_index) +
                    "\t" + 
                    str(ch+1) +
                    "\t" + 
                    str(verse_index) +
                    "\t" + 
                    to_lat(v))
                print(line)
                append_file(TSV_FILE, line)

if __name__ == "__main__": main()
