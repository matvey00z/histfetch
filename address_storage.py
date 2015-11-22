
class AddressStore:
    def __init__(self, address_patterns, last_time, new_patterns,
            storage_filename):
        self.addresses = []
        # list of tuples: [(dictionary_address, [word_patterns])]
        self.address_patterns = address_patterns
        self.start_time = last_time
        self.last_time = last_time
        self.new_patterns = new_patterns
        self.storage_filename = storage_filename

    def feed(self, address, time):
        patterns_to_check = self.address_patterns
        if time:
            time = int(time)
            print
            if time <= self.start_time:
                patterns_to_check = self.new_patterns
            if time > self.last_time:
                self.last_time = time
        for address_pattern_pair in patterns_to_check:
            # check if it is a dictionary
            if not address_pattern_pair[0].search(address):
                continue
            # look for a word being queried in the address
            for pattern in address_pattern_pair[1]:
                match = pattern.match(address)
                if not match:
                    continue
                self.addresses.append((match.group(1), address))
                break
            # May be useful for futher analisys
            # print("No words in address:", address, file=sys.stderr)

    def get_last_time(self):
        return self.last_time

    def print_all(self):
        with open(self.storage_filename, "at") as storage_file:
            for (word, address) in self.addresses:
                print(word.ljust(20, '.') + "[" + address + "]",
                        file=storage_file)
