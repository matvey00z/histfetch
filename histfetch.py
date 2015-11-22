#!/usr/bin/env python3

import sqlite3
import sys
import glob
import os
import re
import json
import shutil
import errno

import address_storage

dbpath = os.path.expanduser("~/.mozilla/firefox/*.default/places.sqlite")
dbpaths = glob.glob(dbpath)
config_directory_path = os.path.expanduser("~/.config/histfetch")
config_path = "/".join([config_directory_path, "config.json"])
default_config_path = "default_config.json"
last_config_path = "/".join([config_directory_path, "last_used_config.json"])

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
    for pattern_pair in config["patterns"].items():
        address_patterns.append(
            (
                re.compile(pattern_pair[0]),
                [re.compile(word_pattern)
                    for word_pattern in pattern_pair[1]]
            )
        )
    return address_patterns

def read_config_file(config_path):
    with open(config_path, "rt") as config_file:
        config = json.load(config_file)
    return config

def get_config_update(old_config, new_config):
    old_patterns = old_config["patterns"]
    new_patterns = new_config["patterns"]
    patterns_update = []
    for new_pattern_pair in new_config.items():
        dictionary_address = new_pattern_pair[0]
        old_word_patterns = old_config.get(dictionary_address, None)
        if not old_word_patterns:
            patterns_update.append(new_pattern_pair)
            continue
        new_word_patterns = new_pattern_pair[1]
        word_update = [pattern for pattern in new_word_patterns
                if pattern not in old_word_patterns]
        if word_update:
            patterns_update.append((dictionary_address, word_update))
    return patterns_update


def create_default_config():
    try:
        os.makedirs(config_directory_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            print("Can't create default config:", sys.exc_info(),
                    file=sys.stderr)
            exit(1)
    shutil.copyfile(default_config_path, config_path)

def main():
    if not os.path.isfile(config_path):
        print("No config fine found; create default", file=sys.stderr)
        create_default_config()
    try:
        config = read_config_file(config_path)
        address_patterns = compile_address_patterns(config)
    except:
        print("Can't read config file:", sys.exc_info(), file=sys.stderr)
        exit(1)
    last_time = 0
    if os.path.isfile(last_config_path):
        last_config = read_config_file(last_config_path)
        config_update = get_config_update(last_config, config)
        last_time = last_config["last_time"]

    storage = address_storage.AddressStore(address_patterns, last_time)
    if not dbpaths:
        print("No paths to import words from", file=sys.stderr)
        sys.exit(1)
    for path in dbpaths:
        import_from_database(path, storage)

    config["last_time"] = storage.get_last_time()
    with open(last_config_path, "wt") as last_config_file:
        json.dump(config, last_config_file)
    storage.print_all()

if __name__ == "__main__":
    main()
