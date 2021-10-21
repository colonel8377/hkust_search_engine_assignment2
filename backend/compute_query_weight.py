"""
Author: YE,Qiming
Date: 2021-10-02 09:17:33
"""
import math

from functools import lru_cache
from blist import sorteddict
from sortedcontainers import SortedKeyList

from backend.parse_text import parse_query
from web import paper_tries, paper_number, paper_word_count, paper_word_weight


def retrive(query, phrases, top_number):
    # handle phrase and words
    texts, querys = parse_query(query)
    text_phrases, query_phrases = [], []
    for phrase in phrases:
        parse_querys = parse_query(phrase)
        query_phrases.append(parse_querys[0])
        text_phrases.append(parse_querys[1])
    tf_phrase, phrase_position = compute_phrase_weight(sorteddict(), query_phrases, 0, [])
    result, tf_idf = generate_weight(texts, tf_phrase, phrase_position)
    top_k_result = result[:top_number]
    show_result(top_k_result, texts, querys, text_phrases, phrase_position)
    return top_k_result


def show_result(top_res, texts, querys, text_phrases, phrase_position):
    for res in top_res:
        print('D' + str(res[0]) + ' score: ' + str(res[1]) + ' magnitude: ' + str(res[2])
              + ' keywords: ' + str(len(paper_word_count[res[0]])))
        print('Five Highest Keywords(After Stem and Stop)')
        for word in paper_word_weight[res[0]][:5]:
            doc_index = paper_tries.get_doc_index(word[0])
            weighted_word = ''
            for doc_id in doc_index:
                weighted_word += ('D' + str(doc_id) + ': ' +
                                  ', '.join([str(doc) for doc in list(doc_index.get(doc_id, ''))]) + ' | ')
            print(word[0] + '  weight: ' + str(round(word[1], 3)) + ' : ' + weighted_word)

    if texts and len(texts) > 0:
        print('single vocabulary')
    for text in texts:
        doc_index = paper_tries.get_doc_index(text)
        print(querys[texts.index(text)])
        for res in top_res:
            print('D ' + str(res[0]) + ': --->' + ', '.join([str(doc) for doc in list(doc_index.get(res[0], ''))]))
    if text_phrases and len(text_phrases) > 0:
        print('phrases')
    for phrase in text_phrases:
        print(' '.join(phrase))
        for res in top_res:
            print('D ' + str(res[0]) + ': --->' +
                  ', '.join([str(doc) for doc in list(phrase_position[text_phrases.index(phrase)].get(res[0], ''))]))


def generate_weight(texts, tf_phrase, phrase_positions):
    result = []
    tf_idf = tf_phrase
    if texts is not None and len(texts) > 0:
        if len(tf_phrase) > 0:
            tf_idf = compute_tf(tf_phrase, texts, 0, len(tf_phrase[tf_phrase.keys()[0]]))
        else:
            tf_idf = compute_tf(sorteddict(), texts, 0, 0)
    df_arr = []
    for phrase_position in phrase_positions:
        df = len(phrase_position)
        idf = math.log((paper_number / (df + 1)), 2.0)
        df_arr.append(idf)
    df_arr = df_arr + [paper_tries.get_idf(text, paper_number) for text in texts]

    # tf_idf = normalize(tf_idf)
    for k in tf_idf:
        tf_idf[k] = generate_tf_idf(tf_idf[k], df_arr)
        cosine = generate_cosine(tf_idf[k], [1.0] * len(tf_idf[k]))
        result.append((k, cosine[0], cosine[1]))
    res = sorted(result, key=lambda x: (x[1]), reverse=True)
    return res, tf_idf


def compute_phrase_weight(possible_paper_dict, query_phrases, pos, phrase_pos: list):
    assert pos >= 0
    if pos >= len(query_phrases):
        return possible_paper_dict, phrase_pos
    phrases = query_phrases[pos]
    phrases_index = {}
    doc_keys = set()
    is_first_loop = True
    for phrase in phrases:
        phrases_index[phrase] = paper_tries.get_doc_index(phrase).copy()
        doc_keys = phrases_index[phrase].keys() if is_first_loop else doc_keys & phrases_index[phrase].keys()
        is_first_loop = False
    if len(doc_keys) < 1:
        for k in possible_paper_dict:
            possible_paper_dict[k].append(0)
        return compute_phrase_weight(possible_paper_dict, query_phrases, pos + 1, phrase_pos)
    else:
        # calculate tf for phrase
        phrase_tf_pos_dict = calculate_phrase_tf(doc_keys, phrases_index, phrases)
        for k in phrase_tf_pos_dict.keys() & possible_paper_dict.keys():
            possible_paper_dict[k].append(len(phrase_tf_pos_dict[k]))
        for k in phrase_tf_pos_dict.keys() - possible_paper_dict.keys():
            possible_paper_dict[k] = list([0] * pos) if pos > 0 else list()
            possible_paper_dict[k].append(len(phrase_tf_pos_dict[k]))
        for k in possible_paper_dict.keys() - phrase_tf_pos_dict.keys():
            possible_paper_dict[k].append(0)
        phrase_pos.append(phrase_tf_pos_dict)
        return compute_phrase_weight(possible_paper_dict, query_phrases, pos + 1, phrase_pos)


def calculate_phrase_tf(doc_keys, phrases_index, phrases):
    phrase_tf_pos_dict = sorteddict()
    for doc_key in doc_keys:
        word_pos_list = [phrases_index[phrase][doc_key] for phrase in phrases]
        count = SortedKeyList()
        next_word_start_pos = {}
        for i in range(len(word_pos_list[0])):
            is_phrase = True
            for j in range(1, len(word_pos_list)):
                start_pos = next_word_start_pos.get(j, 0)
                print(word_pos_list[j])
                try:
                    next_word_start_pos[j] = word_pos_list[j].index(word_pos_list[0][i] + j, start=start_pos) + 1
                except ValueError:
                    next_word_start_pos[j] = 0
                    is_phrase = False
                    break
            if is_phrase:
                count.add(word_pos_list[0][i])
        if count and len(count) > 0:
            phrase_tf_pos_dict[doc_key] = count
    return phrase_tf_pos_dict


@lru_cache(maxsize=10)
def generate_vector(text):
    return paper_tries.get_doc_index(text)


def compute_tf(possible_paper_dict, texts, i, basic_length):
    assert i >= 0
    if i >= len(texts):
        return possible_paper_dict
    vocabulary = texts[i]
    doc_index = paper_tries.get_doc_index(vocabulary)
    for k in doc_index.keys() & possible_paper_dict.keys():
        possible_paper_dict[k].append(len(doc_index[k]))
    for k in doc_index.keys() - possible_paper_dict.keys():
        possible_paper_dict[k] = list([0] * (i + basic_length))
        possible_paper_dict[k].append(len(doc_index[k]))
    for k in possible_paper_dict.keys() - doc_index.keys():
        possible_paper_dict[k].append(0)
    return compute_tf(possible_paper_dict, texts, i + 1, basic_length)


def generate_cosine(vector1, vector2):
    assert vector1 is not None and vector2 is not None and len(vector1) == len(vector2)
    dot = sum([a * b for a, b in zip(vector1, vector2)])
    norm_a = sum([a * a for a in vector1])
    norm_b = sum([b * b for b in vector2])
    cos_sim = dot / (math.sqrt(norm_a) * math.sqrt(norm_b))
    return cos_sim, norm_a


def generate_tf_idf(tf, idf):
    assert tf is not None and idf is not None and len(tf) == len(idf)
    result = []
    for i in range(len(tf)):
        result.append(tf[i] * idf[i])
    return result


def normalize(tf):
    from web import paper_word_count
    for k in tf:
        for i in range(len(tf[k])):
            tf[k][i] /= paper_word_count[k]
    return tf
