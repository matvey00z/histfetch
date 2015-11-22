#!/usr/bin/env python3

import sqlite3
import sys
import glob
import os
import re

import address_storage

dbpath = os.path.expanduser("~/.mozilla/firefox/*.default/places.sqlite")
dbpaths = glob.glob(dbpath)

def isSQLite3(filename):
    from os.path import isfile, getsize

    if not isfile(filename):
        return False
    if getsize(filename) < 100: # SQLite database file header is 100 bytes
        return False

    with open(filename, "rb") as sq_file:
        header = sq_file.read(100)

    return header[:16] == b"SQLite format 3\x00"


def import_from_database(path, address_storage):
    if not isSQLite3(path):
        print("No such SQLite3 database:", path, file=sys.stderr)
        sys.exit(1)
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cmd = "SELECT url,last_visit_date FROM moz_places"
    cursor.execute(cmd)
    for response in cursor:
        address_storage.feed(response[0], response[1])

def main():
    dictionary_address = "www.oxfordlearnersdictionaries.com"
    address_patterns = [
        (
            re.compile(dictionary_address),
            [
                re.compile(".*/definition/.*?q=(.*)"),
                re.compile(".*/definition/.*/(.*)#"),
            ]
        )
    ]
    storage = address_storage.AddressStore(address_patterns)
    if not dbpaths:
        print("No paths to import words from", file=sys.stderr)
        sys.exit(1)
    for path in dbpaths:
        import_from_database(path, storage)
    storage.print_all()

if __name__ == "__main__":
    main()
