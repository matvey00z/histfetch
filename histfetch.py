#!/usr/bin/env python3

import sqlite3
import sys
import glob
import os
import re
import json

import address_storage

dbpath = os.path.expanduser("~/.mozilla/firefox/*.default/places.sqlite")
dbpaths = glob.glob(dbpath)
config_path = os.path.expanduser("~/.config/histfetch/config.json")

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

def compile_address_patterns(config):
    address_patterns = []
    for pattern_pair in config["patterns"]:
        address_patterns.append(
            (
                re.compile(pattern_pair["dictionary_address"]),
                [re.compile(word_pattern)
                    for word_pattern in pattern_pair["word_patterns"]]
            )
        )
    return address_patterns

def main():
    try:
        with open(config_path, "rt") as config_file:
            config = json.load(config_file)
        address_patterns = compile_address_patterns(config)
    except:
        print("Can't read config file:", sys.exc_info(), file=sys.stderr)
        exit(1)
    storage = address_storage.AddressStore(address_patterns)
    if not dbpaths:
        print("No paths to import words from", file=sys.stderr)
        sys.exit(1)
    for path in dbpaths:
        import_from_database(path, storage)
    storage.print_all()

if __name__ == "__main__":
    main()
