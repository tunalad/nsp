# nsp -- Serbian Bible on the Command Line
A command-line tool for searching and reading the Bible in the new Serbian translation.

Forked from https://github.com/LukeSmithxyz/kjv.git with some changes made for setting up other translations.

## Usage
```
    usage: ./nsp [flags] [reference...]

      -l      list books
      -W      no line wrap
      -h      show help

      Reference types:
          <Book>
              Individual book
          <Book>:<Chapter>
              Individual chapter of a book
          <Book>:<Chapter>:<Verse>[,<Verse>]...
              Individual verse(s) of a specific chapter of a book
          <Book>:<Chapter>-<Chapter>
              Range of chapters in a book
          <Book>:<Chapter>:<Verse>-<Verse>
              Range of verses in a book chapter
          <Book>:<Chapter>:<Verse>-<Chapter>:<Verse>
              Range of chapters and verses in a book

          /<Search>
              All verses that match a pattern
          <Book>/<Search>
              All verses in a book that match a pattern
          <Book>:<Chapter>/<Search>
              All verses in a chapter of a book that match a pattern
```
## Notes
- The Bible was obtained via a data scraper I've written (found in `src`), so there might be some mistakes in the text.
- All books are named with their English titles. This is primarily because not many people are willing to set up their keyboards in Cyrillic. I might write Serbian titles in Latin later.
- The `src` directory contains source code for scraping from BibleGateway. 

## Install
Install `nsp` by running:

```
git clone https://github.com/tunalad/nsp.git
cd nsp
sudo make install
```
