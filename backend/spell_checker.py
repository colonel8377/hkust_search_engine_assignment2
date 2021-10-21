from functools import lru_cache
from spellchecker import SpellChecker
from web import paper_dict


@lru_cache(maxsize=10)
def init_name():
    spell = SpellChecker('en')
    partial_names = set()
    for paper in paper_dict:
        author_names = [author_name for author_name in paper['authors']]
        for author_name in author_names:
            for partial_name in author_name.split(' '):
                partial_names.add(partial_name.lower())
                partial_names.add(author_name.lower())
    spell.word_frequency.load_words(list(partial_names))
    return spell


if __name__ == '__main__':
    sp = SpellChecker('en')
    misspelled = sp.unknown(['something', 'is', 'hapenning', 'here'])
    for word in misspelled:
        # Get the one `most likely` answer
        print(sp.correction(word))

        # Get a list of `likely` options
        print(sp.candidates(word))
