from backend.initialize_search_tries import analysis_text
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords


def parse_query(text: str):
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    texts = analysis_text(text)
    return [ps.stem(text.lower().strip()) for text in texts if text.lower().strip() not in stop_words], \
           [text.lower().strip() for text in texts if text.lower().strip() not in stop_words]


def parse_single_word(text: str):
    ps = PorterStemmer()
    texts = analysis_text(text)
    return [ps.stem(text.lower().strip()) for text in texts if text.lower().strip() not in stopwords], \
           [text.lower().strip() for text in texts if text.lower().strip() not in stopwords]