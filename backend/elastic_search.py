import logging
import os

from elasticsearch import Elasticsearch

from web import paper_dict

es_host = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')
es = Elasticsearch([es_host], maxsize=25)

logger = logging.getLogger(__name__)


def phrase_suggest(index, prefix):
    body = {
        'suggest': {
            'text': prefix,
            'phrase_suggest': {
                'phrase': {
                    'field': 'phrase_suggest.trigram',
                    'size': 5,
                    'gram_size': 3,
                    'direct_generator': [{
                        'field': 'phrase_suggest.trigram',
                        'suggest_mode': 'always'
                    }, {
                        'field': 'phrase_suggest.reverse',
                        'suggest_mode': 'always',
                        'pre_filter': 'reverse',
                        'post_filter': 'reverse'
                    }],
                    'highlight': {
                        'pre_tag': '<em>',
                        'post_tag': '</em>'
                    }
                }
            }
        }
    }
    titles = []
    try:
        resps = es.search(index=index, body=body)
        for resp in resps['suggest']['phrase_suggest']:
            for paper in resp['options']:
                titles.append(paper['text'])
        return titles
    except:
        logger.error('elasticsearch.exceptions.TransportError')


def prefix_suggest(index, prefix):
    body = {
        'suggest': {
            'phrase_suggest': {
                'prefix': prefix,
                'completion': {
                    'field': 'phrase_suggest',
                    'fuzzy': {
                        'fuzziness': 5,
                    }
                }
            }
        }
    }
    titles = []
    resps = None
    try:
        resps = es.search(index=index, body=body)
        for resp in resps['suggest']['phrase_suggest']:
            for paper in resp['options']:
                titles.append(paper['_source']['title'])
        return titles
    except:
        logger.error('elasticsearch.exceptions.TransportError')


def create_synonym_index(index):
    settings = {
        'number_of_shards': 3,
        'number_of_replicas': 2,
        'index': {
            'analysis': {
                'filter': {
                    'synonym': {
                        'type': 'synonym',
                        'synonyms_path': 'analysis/synonym.txt'
                    },
                    'english_stop': {
                        'type': 'stop',
                        'stopwords': '_english_'
                    },
                    'english_stemmer': {
                        'type': 'stemmer',
                        'language': 'english'
                    },
                    'english_possessive_stemmer': {
                        'type': 'stemmer',
                        'language': 'possessive_english'
                    },
                    'autocomplete_filter': {
                        'type': 'edge_ngram',
                        'min_gram': 1,
                        'max_gram': 20
                    },
                    'shingle': {
                        'type': 'shingle',
                        'min_shingle_size': 2,
                        'max_shingle_size': 3
                    }
                },
                'analyzer': {
                    'synonym_standard_analyzer': {
                        'tokenizer': 'standard',
                        'filter': 'synonym'
                    },
                    'synonym_english_analyzer': {
                        'tokenizer': 'standard',
                        'filter': ['synonym',
                                   'lowercase',
                                   'english_possessive_stemmer',
                                   'english_stop',
                                   'english_stemmer']
                    },
                    'autocomplete': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': [
                            'synonym',
                            'lowercase',
                        ]
                    },
                    'trigram': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'shingle']
                    },
                    'reverse': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'reverse']
                    }

                },
            }
        }
    }
    mappings = {
        'properties': {
            'abstract': {
                'type': 'text',
                'index': 'true',
                'analyzer': 'synonym_english_analyzer',
                'search_analyzer': 'english',
                'copy_to': 'phrase_suggest',
            },
            'title': {'type': 'text',
                      'index': 'true',
                      'analyzer': 'synonym_standard_analyzer',
                      'search_analyzer': 'english', 'copy_to': 'phrase_suggest'},
            'author': {'type': 'text',
                       'index': 'true',
                       'analyzer': 'standard',
                       'copy_to': 'phrase_suggest'},
            'year': {'type': 'date',
                     'index': 'true',
                     'format': 'yyyy',
                     'copy_to': 'phrase_suggest'},
            'phrase_suggest': {
                'type': 'completion',
                'index': 'true',
                'analyzer': 'autocomplete',
                'search_analyzer': 'synonym_standard_analyzer',
                'preserve_separators': False,

            }
        }
    }
    es.indices.create(index=index, body={'settings': settings, 'mappings': mappings})


def create_simple_index(index):
    settings = {
        'number_of_shards': 3,
        'number_of_replicas': 2,
        'index': {
            'max_shingle_diff': 10,
            'analysis': {
                'filter': {
                    'synonym': {
                        'type': 'synonym',
                        'synonyms_path': 'analysis/synonym.txt'
                    },
                    'english_stop': {
                        'type': 'stop',
                        'stopwords': '_english_'
                    },
                    'english_stemmer': {
                        'type': 'stemmer',
                        'language': 'english'
                    },
                    'english_possessive_stemmer': {
                        'type': 'stemmer',
                        'language': 'possessive_english'
                    },
                    'autocomplete_filter': {
                        'type': 'edge_ngram',
                        'min_gram': 1,
                        'max_gram': 20
                    },
                    'shingle': {
                        'type': 'shingle',
                        'min_shingle_size': 2,
                        'max_shingle_size': 5,
                    }
                },
                'analyzer': {
                    'synonym_standard_analyzer': {
                        'tokenizer': 'standard',
                        'filter': 'synonym'
                    },
                    'synonym_english_analyzer': {
                        'tokenizer': 'standard',
                        'filter': ['synonym',
                                   'lowercase',
                                   'english_possessive_stemmer',
                                   'english_stop',
                                   'english_stemmer']
                    },
                    'autocomplete': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': [
                            'synonym',
                            'lowercase',
                        ]
                    },
                    'trigram': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'shingle']
                    },
                    'reverse': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'reverse']
                    }
                },
            }
        }
    }
    mappings = {
        'properties': {
            'abstract': {'type': 'text', 'index': 'true', 'analyzer': 'english', 'copy_to': 'phrase_suggest'},
            'title': {'type': 'text', 'index': 'true', 'analyzer': 'standard', 'copy_to': 'phrase_suggest'},
            'author': {'type': 'text', 'index': 'true', 'analyzer': 'whitespace', 'copy_to': 'phrase_suggest'},
            'year': {'type': 'date', 'index': 'true', 'format': 'yyyy'},
            'phrase_suggest': {
                'type': 'text',
                'fields': {
                    'trigram': {
                        'type': 'text',
                        'analyzer': 'trigram',
                        'search_analyzer': 'synonym_standard_analyzer',
                    },
                    'reverse': {
                        'type': 'text',
                        'analyzer': 'reverse',
                        'search_analyzer': 'synonym_standard_analyzer',

                    }
                }
            }
        }
    }
    es.indices.create(index=index, body={'settings': settings, 'mappings': mappings})


def bulk_simple_data(index):
    if not es.indices.exists(index=index):
        from elasticsearch import helpers
        create_simple_index(index)
        es_insert_paper = paper_dict.copy()
        for paper in es_insert_paper:
            paper['authors'] = ' '.join(paper['authors'])
        # we must include id because there is duplicate data.
        source = [{'_op_type': 'create',
                   '_index': index,
                   '_id': i,
                   '_type': '_doc',
                   '_source': es_insert_paper[i],
                   } for i in range(len(es_insert_paper))]
        res = helpers.bulk(es, source)
        print(res)
        es.indices.refresh(index=index)


def bulk_synonym_data(index):
    if not es.indices.exists(index=index):
        from elasticsearch import helpers
        create_synonym_index(index)
        es_insert_paper = paper_dict.copy()
        for paper in es_insert_paper:
            paper['authors'] = ' '.join(paper['authors'])
        # we must include id because there is duplicate data.
        source = [{'_op_type': 'create',
                   '_index': index,
                   '_id': i,
                   '_type': '_doc',
                   '_source': es_insert_paper[i],
                   } for i in range(len(es_insert_paper))]
        res = helpers.bulk(es, source)
        print(res)
        es.indices.refresh(index=index)


if __name__ == '__main__':
    synonym_idx = 'paper_search_engine_synonym'
    simple_idx = 'paper_search_engine'
    print(es.indices.exists(index=synonym_idx))
    bulk_simple_data(simple_idx)
    bulk_synonym_data(synonym_idx)
    # prefix_suggest(synonym_idx, 'kno')
