# Search Engine
###### A single but not simple searching framework.
## Material
> 778 esaays from public resources (paper.json)
## Highlight
- **Fancy Data Structure (Tries/Blist/Sortedlist/Sorteddict/SortedKeyList)**
- **Fix original cross-fields problem**
- **Ran in real server (k8s or docker)**
- **Seperate frontend and backend system (nginx)**
- **Auto-complete and search prediction (elasticsearch)**
- **Typo correction**
- **Pre-built index (whoosh)**
- **Various searching methods**kooooooooooooofo
## Search
### original tf idf searching process
1. Original Search
> Original search programming code is in the se_search.py and there is also a main function entry in this file.
2. Query Content
> The query content in the search box will be extracted regularly according to the phrase and single word, and searched according to different query methods
3. Data Structure
> We use dictionary tries to save space (though this is an inefficient ways to find the index).
4. For Phrases 
> I calculate their tf-idf dynamically. Whenever there is a new query for a phrase, we will recalculate its tf-idf in the text.
5. For Words 
> I use tries to get the tf-idf corresponding to each word.
6. Calculation Process
> Main calculation will be done by compute_weight.py
7. Original Calculation Function
```
def original_tf_idf(query, top_number):
    from compute_weight import retrive
    from web import paper_dict
    single_words = re.sub(r'"([^"]*)"', '', query)
    phrases = re.findall(r'"([^"]*)"', query)
    result = retrive(single_words, phrases, top_number)
    top5_res = [paper_dict[item] for item in [res[0] for res in result]]
    return top5_res
```
### whoosh searching
#### Schema
```
schema = Schema(title=TEXT(stored=True, analyzer=FancyAnalyzer()),
                authors=KEYWORD(stored=True, scorable=True, analyzer=SimpleAnalyzer(), commas=True),
                abstract=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                year=fields.DATETIME(stored=True))
```
#### Query
Whoosh is a fast, featureful full-text indexing and searching library implemented in pure Python. 
```
whoosh_query(text, top_number)
```
#### Index
- Ordinary TF-IDF
1. I use tries to store all the stemming words (exclude stop words). Each node in tries stores a sorted dictionary, whose keys are the position or array subscripts of the paper in the file and values denotes the strict order of words in one document, to represent a word's term frequency in one file.
2. For each paper, every information (including authors' name and published year) is stored in the paper_tries, which is decorated by "@lru.cache" to increase calculation speeds.
3. For each list/dict, I install the package blist, which enables program to find exactly item in arrays/to sort the data in O(logn) time.
4. To compress the storage, I use tries instead of dictionary to represent the data structure. (Partly becuase I ran the flask application in docker container, without no-sql database, serialization of data in python is really a waste of time and may lead to out of memory)
- whoosh
1. For whoosh, I use a different way to represent the information from paper.json.
## Starting up
###Docker
#### For window users:
##### 1. Increase virtual limits
```
# enter the wsl
wsl
# (if there is not enough v-mem)
sudo sysctl -w vm.max_map_count=524288 
# docker
docker-compose build
docker-compose up
# wait
```
##### 2. Check Containers
- [kibana](https://www.elastic.co/kibana/) : http://localhost:5601
- [elasticsearch](https://www.elastic.co/elasticsearch/) : http://localhost:9200
- [nginx](https://www.nginx.com/) : http://localhost:8000
- [Flask](https://flask.palletsprojects.com/en/2.0.x/) : http://localhost:4000
</br>If you would like to allow anyone in the ust to assess this search engine, adjusting nginx information and typing your ipv4-address (mostly, this is started with 10.29*) under the local area framework, and then you may allow other to login in your search-engine and kibana.
  </br>If you failed to connecnt to the kibana container, please check the firewall or network configuration of the machine.
##### 3. Initialize project
###### Quick Start up
- whoosh.py
```
if __name__ == '__main__':
    # methods to init index directory
    init_schema_dir()
```
- es.py
```
if __name__ == '__main__':
    synonym_idx = 'paper_search_engine_synonym'
    simple_idx = 'paper_search_engine'
    print(es.indices.exists(index=synonym_idx))
    bulk_simple_data(simple_idx)
    bulk_synonym_data(synonym_idx)
    # prefix_suggest(synonym_idx, 'kno')
```
Before sending data to elasticsearch, you need to specify the IP address and port of the elasticsearch server. More specific, 
- For Local Environment
```
es = Elasticsearch(['http://127.0.0.1:9200'], maxsize=25)
```
- For Docker Flask(or Server)
```
es_host = os.environ['ELASTICSEARCH_URL']
es = Elasticsearch([es_host], maxsize=25)
```

##### Auto Correction and Completion
1. When users are typing words, search engine may assume that words/sentence displaying on the screen are parts of prefix of query. We may search such incomplete words/sentence fuzzily, and return the matching results to increase the precision of the searching process. 
2. When there is no matching result, we may assume that the users have mistakenly misspelled the query phrases or words. And the searching engine can make response to such issues. Here we only response a "Did you mean field." to assist users to correct their words quicly.

![avatar](https://raw.githubusercontent.com/colonel8377/advanced-algorithms/master/img/d.png)

##### Customization
- elasticsearch
<p>Restful Api: Elasticsearch accpts restful api, which I have set up in es.py. You may rewrite some requests to create different index.</p>
- whoosh
<p>Whoosh Schema: Here I assume that the author's name and paper's publishing year are key words and can not be stemming by the engine.</p>
Everything is all right, have fun!

### Contact
###### YE, Qiming
- qyeaf@connect.ust.hk
- colonelaureliano8379@gmail.com
- If you have any questions about starting up program, feel free to contact me.
