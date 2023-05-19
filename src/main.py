#!/usr/bin/env python
# biblegateway.com scrapper, main logic in main()
# tested only with NSP, you probably have to make some changes in `get_verse` and `get_verses`
# this script takes ~12 minutes to scrap the whole bible

import re
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs

def get_soup(url):# {{{
    # main soup
    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    return soup# }}}

def get_passasge(passage, bible_version = "nsp"):# {{{
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
        'Revelation': 'Rev'
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
    TSV_FILE = "nsp.tsv"
    bible_version = "NSP" #"ERV-SR"
    #books = get_books_list("New-Serbian-Translation-NSP-Bible")
    books = get_books_list("King-James-Version-KJV-Bible") # value from biblegateway.com/versions/_____

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
                line = (book["name"] +
                      "\t" + 
                      get_short_name(book["name"]) +
                      "\t" + 
                      str(book_index) +
                      "\t" + 
                      str(ch+1) +
                      "\t" + 
                      str(verse_index) +
                      "\t" + 
                      v)
                print(line)
                append_file(TSV_FILE, line)

if __name__ == "__main__": main()
