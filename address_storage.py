
class AddressStore:
    def __init__(self, address_patterns):
        self.addresses = []
        # list of tuples: [(dictionary_address, [word_patterns])]
        self.address_patterns = address_patterns

    def feed(self, address, time):
        for address_pattern_pair in self.address_patterns:
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

    def print_all(self):
        for (word, address) in self.addresses:
            print(word.ljust(20, '.') + "[" + address + "]")
