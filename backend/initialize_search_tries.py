def parse_json(file_name: str):
    assert file_name is not None and len(file_name) != 0
    with open(file_name, 'r') as load_f:
        import json
        load_dict = json.load(load_f)
        return load_dict


def analysis_text(text: str):
    import re
    from nltk.tokenize import word_tokenize
    text = re.sub(r'[~`!@#$%^&*()_\-+=|\\{\}\[\]:;\"\'<>,.?/·！￥…（）—【】、？《》，。]+', ' ', text).replace('n’t', ' not ')
    word_tokens = word_tokenize(text)
    return word_tokens


def analysis_authors(authors: list):
    res = []
    for author in authors:
        import codecs
        import re
        for name in re.split(r'[\. -]+', author):
            import translitcodec
            import codecs
            name = codecs.encode(name.lower(), 'translit/long').strip()
            res.append(name)
    return res


def init_tries(paper_dict, is_only_abstract):
    from tries import Trie
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    paper_tries = Trie()
    paper_word_count = {}
    for i in range(len(paper_dict)):
        word_count = {}
        year_author = [paper_dict[i]['year']]
        year_author.extend(analysis_authors(paper_dict[i]['authors']))
        main_body = paper_dict[i]['abstract']
        if not is_only_abstract:
            main_body = paper_dict[i]['title'] + ' ' + paper_dict[i]['abstract']
        analysis_texts = analysis_text(main_body)
        if is_only_abstract:
            for j in range(len(analysis_texts)):
                if analysis_texts[j].lower() not in stop_words:
                    stem_stop_word = ps.stem(analysis_texts[j].lower().strip())
                    paper_tries.insert(stem_stop_word, i, j)
                    word_count[stem_stop_word] = word_count.get(stem_stop_word, 0) + 1
        else:
            for j in range(len(year_author)):
                paper_tries.insert(year_author[j], i, j)
                word_count[year_author[j]] = word_count.get(year_author[j], 0) + 1
            for j in range(len(analysis_texts)):
                if analysis_texts[j].lower() not in stop_words:
                    stem_stop_word = ps.stem(analysis_texts[j].lower().strip())
                    paper_tries.insert(stem_stop_word, i, j + len(year_author))
                    word_count[stem_stop_word] = word_count.get(stem_stop_word, 0) + 1
        paper_word_count[i] = word_count
    return paper_tries, paper_word_count


def init_weighted_keywords(paper_tries, paper_word_count):
    from blist import sortedlist
    paper_word_weight = {}
    paper_number = len(paper_word_count)
    for doc in paper_word_count:
        doc_weight = sortedlist(key=lambda x: (-x[1], x[0]))
        for word in paper_word_count[doc]:
            doc_weight.add((word, paper_tries.get_idf(word, paper_number) * paper_tries.get_tf(word, doc)))
        paper_word_weight[doc] = doc_weight
    return paper_word_weight
