# nsp - Serbian Bible on the Command Line

A command-line tool for searching and reading the Bible in the new Serbian translation.

Forked from https://github.com/LukeSmithxyz/kjv.git with some changes made for setting up other translations.

## Usage

```
    usage: nsp [flags] [reference...]

      -l      list books
      -r      random verse
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

      Interactive mode commands:
          list
                list books
          help
                show help
```

## Notes

-   All books are in latin
-   The Bible was obtained via a data scraper I've written (found in `src`), so there might be some mistakes in the text.

## Install

Install `nsp` by running:

```
git clone https://github.com/tunalad/nsp.git
cd nsp
sudo make install
```
