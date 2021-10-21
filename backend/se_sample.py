"""
Author: JasonYU
Date: 2020-10-02 09:17:33
LastEditTime: 2020-10-04 10:00:43
FilePath: .\SE\flask_se\backend\se_sample.py
"""


def original_tf_idf(query, top_number):
    """
    query:[string]
    top_number: length of result array
    return: list of dict, each dict is a paper record of the original dataset
    """
    from compute_query_weight import retrive
    from web import paper_dict
    import re
    single_words = re.sub(r'"([^"]*)"', '', query)
    phrases = re.findall(r'"([^"]*)"', query)
    result = retrive(single_words, phrases, top_number)
    top_res = [paper_dict[item] for item in [res[0] for res in result]]
    return top_res


def phrase_suggest(phrases):
    import spell_checker
    sp = spell_checker.init_name()
    misspell = sp.unknown(phrases)
    resp = []
    for word in misspell:
        resp.append(word + ' ---> ' + sp.correction(word) + '. ' + '</br>')
        resp.append(word + ' ---> ' + ', '.join(sp.candidates(word)) + '. ' + '</br>')
    return resp


def suggest_api(query):
    """
    query:[string]
    return: list of title
    This api is for auto-completion/language correction purpose
    """
    from elastic_search import prefix_suggest, phrase_suggest
    titles = prefix_suggest('paper_search_engine_synonym', query)
    if titles and len(titles) > 0:
        resp = ['<em>Recommendation title</em>']
        resp.extend(titles)
        return resp
    phrase = phrase_suggest('paper_search_engine', query)
    if phrase and len(phrase) > 0:
        resp = ['<em> No recommendation title. Did you mean? </em>']
        resp.extend(phrase)
        return resp
    return ['<em> No recommendation title.</em>']


def search_api(query):
    """
    query:[string] 
    return: list of dict, each dict is a paper record of the original dataset
    I have implemented this process with two methods--whoosh, a third party package, and code written by myself.
    Have fun!!
    """
    from whoosh_search import whoosh_query
    top_number = 10
    # top10_res = original_tf_idf(query, top_number)
    top_k_res = whoosh_query(query, top_number)
    if not top_k_res or len(top_k_res) < top_number:
        phrase = phrase_suggest(str(query).lower().strip().split(' '))
        return [{'title': 'Did you mean?', 'authors': ['Opps~Mispelling Found...'], 'year': '', 'abstract': ''.join(phrase)}]
    return top_k_res


if __name__ == "__main__":
    # this is for testing purpose
    text = '"Dialogue Act Classification"'
    original_tf_idf(text, 10)
