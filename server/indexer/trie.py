import argparse
import os
from collections import deque

class TrieNode:
    def __init__(self, text=''):
        self.text = text
        self.children = dict()
        self.value = None

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, text, value):
        current = self.root

        for i, c in enumerate(text):
            if c not in current.children:
                prefix = text[0:i+1]
                current.children[c] = TrieNode(prefix)
            current = current.children[c]

        current.value = value

    def find(self, query):
        current = self.root

        for c in query:
            if c not in current.children:
                return None
            current = current.children[c]

        return current.value

    def find_starts_with(self, query):
        results = []

        current = self.root
        for c in query:
            if not c in current.children:
                return results

            current = current.children[c]

        # BFS
        q = deque()
        q.append(current)
        while len(q) > 0:
            current = q.popleft()
            if current.value is not None:
                results.append(current.value)

            for node in current.children.values():
                q.append(node)

        return results

def main(args):
    assert os.path.exists(args.store_file)
    assert os.path.exists(args.query_file)

    the_trie = Trie()
    with open(args.store_file, 'r') as fr:
        for i, line in enumerate(fr.readlines()):
            tokens = line.split()
            value = tokens[-1]

            try:
                value = int(value)
            except ValueError as _:
                print(f'line {i} does not end with an integer: {line}')

            value_index = line.rfind(str(value))
            assert value_index > 0
            if value_index == 0:
                print(f'line {i} has no actualy contents other than the value')
                continue

            text = line[0:value_index]
            the_trie.insert(text, value)

            print(f'Inserted: "{text}" with value {value}')

    with open(args.query_file, 'r') as fr:
        for i, line in enumerate(fr.readlines()):
            sanitized_line = line.strip()

            found = the_trie.find(sanitized_line)
            found = "None" if found is None else str(found)
            print(f'query {sanitized_line} found {found}')

            starts_with = the_trie.find_starts_with(sanitized_line)
            if len(starts_with) > 0:
                print(f'query {sanitized_line} has matching starting values:')
                print(starts_with)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--store-file', type=str, help='File terms & values to store')
    parser.add_argument('--query-file', type=str, help='File w/list of terms to query')

    main(parser.parse_args())
