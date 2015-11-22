import sys
import os
import re
import json
import shutil
import errno

config_directory_path = os.path.expanduser("~/.config/histfetch")
config_path = "/".join([config_directory_path, "config.json"])
default_config_path = "default_config.json"
last_config_path = "/".join([config_directory_path, "last_used_config.json"])

def create_default_config():
    try:
        os.makedirs(config_directory_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            print("Can't create default config:", sys.exc_info(),
                    file=sys.stderr)
            exit(1)
    shutil.copyfile(default_config_path, config_path)

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

class ConfigParser:
    def __init__(self):
        if not os.path.isfile(config_path):
            print("No config fine found; create default", file=sys.stderr)
            create_default_config()
        try:
            self.config = read_config_file(config_path)
            self.address_patterns = compile_address_patterns(self.config)
        except:
            print("Can't read config file:", sys.exc_info(), file=sys.stderr)
            exit(1)
        self.config_update = []
        self.last_time = 0
        if os.path.isfile(last_config_path):
            self.last_config = read_config_file(last_config_path)
            self.config_update = get_config_update(self.last_config, self.config)
            self.last_time = self.last_config["last_time"]

    def write_last_config(self):
        with open(last_config_path, "wt") as last_config_file:
            json.dump(self.config, last_config_file)
