from blist import sorteddict
from sortedcontainers import SortedKeyList


class Trie:
    def __init__(self):
        self.children = sorteddict()
        self.isEnd = False
        self.doc_index = None

    def search_prefix(self, prefix: str) -> "Trie":
        node = self
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def insert(self, word: str, index: int, pos: int) -> None:
        node = self
        for ch in word:
            if ch not in node.children:
                node.children[ch] = Trie()
            node = node.children[ch]
        node.isEnd = True
        node.set_doc_index(index, pos)

    def search(self, word: str) -> "Trie":
        node = self.search_prefix(word)
        if node is not None and node.isEnd:
            return node
        else:
            return None

    def starts_with(self, prefix: str) -> bool:
        return self.search_prefix(prefix) is not None

    def set_doc_index(self, index: int, pos: int):
        if self.doc_index is None:
            self.doc_index = sorteddict()
        if index not in self.doc_index:
            self.doc_index[index] = SortedKeyList()
        self.doc_index[index].add(pos)

    def get_doc_index(self, word: str):
        node = self.search(word)
        if node and node.doc_index:
            return node.doc_index
        else:
            return sorteddict()

    def get_df(self, word) -> int:
        node = self.search(word)
        if node and node.doc_index:
            return len(node.doc_index)
        else:
            return 0

    def get_tf(self, word, index: int) -> int:
        node = self.search(word)
        if node and node.doc_index and index in node.doc_index:
            return len(node.doc_index[index])
        else:
            return 0

    def get_idf(self, word, number) -> float:
        import math
        node = self.search(word)
        if node and node.doc_index:
            # avoid zeropaper_number
            return math.log((number / (len(node.doc_index) + 1)), 2.0)
        else:
            return math.log(number, 2.0)


if __name__ == '__main__':
    from web import paper_tries, paper_number
    print(paper_tries.get_doc_index('knowledg')[320])
