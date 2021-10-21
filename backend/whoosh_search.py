import logging

from whoosh.fields import Schema

from web import paper_dict

logger = logging.getLogger(__name__)


def init_schema_dir():
    import os.path
    import translitcodec
    import codecs
    from whoosh import fields
    from whoosh.analysis import StemmingAnalyzer, FancyAnalyzer, SimpleAnalyzer
    from whoosh.index import create_in
    from whoosh.fields import TEXT, KEYWORD
    schema = Schema(
                    title=TEXT(stored=True, analyzer=FancyAnalyzer()),
                    authors=KEYWORD(stored=True, scorable=True, analyzer=SimpleAnalyzer(), commas=True),
                    abstract=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                    year=fields.DATETIME(stored=True))
    indexdir = 'indexdir/'
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
    ix = create_in(indexdir, schema)
    writer = ix.writer()
    for paper in paper_dict:
        title, authors, abstract, year = paper['title'], paper['authors'], paper['abstract'], paper['year']
        authors = ','.join([codecs.encode(author, 'translit/long') for author in authors])
        writer.add_document(title=title, authors=authors, abstract=abstract, year=year)
    writer.commit()


def whoosh_query(text, top_number):
    from whoosh import index, scoring
    from whoosh.qparser import MultifieldParser
    ix = index.open_dir(dirname='/opt/apps/search_engine/indexdir')
    qp = MultifieldParser(["title", "authors", "abstract", "year"], schema=ix.schema)
    q = qp.parse(text)
    top_res = []
    with ix.searcher(weighting=scoring.TF_IDF()) as s:
        results = s.search(q,  limit=top_number)
        for result in results:
            logger.info(' '.join(['title:', str(result['title']), ',', 'score', str(result.score)]))
            paper = {}
            for k in result.keys():
                paper[k] = result.get(k)
            top_res.append(paper)
        return top_res


if __name__ == '__main__':
    # methods to init index directory
    init_schema_dir()
