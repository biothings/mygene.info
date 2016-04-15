from elasticsearch.exceptions import NotFoundError

from biothings.settings import BiothingSettings
from biothings.utils.es import get_es
biothing_settings = BiothingSettings()

class UserFilters(object):
    def __init__(self):
        self.conn = get_es(biothing_settings.es_host) 
        self.ES_INDEX_NAME = 'userfilters'
        self.ES_DOC_TYPE = 'filter'
        self._MAPPING = {
            "dynamic": False,
            "properties": {}
        }   # this mapping disables indexing completely since we don't need it.

    def create(self):
        print("Creating index...",)
        print(self.conn.create_index(self.ES_INDEX_NAME))
        print("Updating mapping...",)
        print(self.conn.put_mapping(self.ES_DOC_TYPE,
                                    self._MAPPING,
                                    [self.ES_INDEX_NAME]))

    def add(self, name, id_list=[], id_field="entrezgene", raw_filter=None):
        '''add a named filter.'''
        _filter = None
        if raw_filter:
            _filter = raw_filter
        elif id_list and id_field:
            _filter = {
                "terms": {id_field: id_list}
            }
        if _filter:
            print('Adding filter "{}"...'.format(name),)
            _doc = {'_id': name,
                    'filter': _filter}
            print(self.conn.index(_doc, self.ES_INDEX_NAME,
                                  self.ES_DOC_TYPE,
                                  id=_doc['_id']))
        else:
            print("No filter to add.")

    def get(self, name):
        '''get a named filter.'''
        try:
            return self.conn.get(self.ES_INDEX_NAME, name, self.ES_DOC_TYPE)['_source']
        except NotFoundError:
            return None

    def count(self):
        n = self.conn.count(None, self.ES_INDEX_NAME, self.ES_DOC_TYPE)['count']
        return n

    def get_all(self, skip=0, size=1000):
        '''get all named filter.'''
        print('\ttotal filters: {}'.format(self.count()))
        q = {"query": {"match_all": {}}}
        res = self.conn.search_raw(q, indices=self.ES_INDEX_NAME, doc_types=self.ES_DOC_TYPE,
                                   **{"from": str(skip), "size": str(1000)})
        return [hit['_source'] for hit in res.hits.hits]

    def delete(self, name, noconfirm=False):
        '''delete a named filter.'''
        _filter = self.get(name)
        if _filter:
            msg = 'Found filter "{}". Continue to delete it?'.format(name)
            if noconfirm or ask(msg) == 'Y':
                print('Deleting filter "{}"...'.format(name),)
                print(self.conn.delete(self.ES_INDEX_NAME, self.ES_DOC_TYPE, name))
        else:
            print('Filter "{}" does not exist. Abort now.'.format(name))

    def rename(self, name, newname):
        '''"rename" a named filter.
           Basically, this needs to create a new doc and delete the old one.
        '''
        _filter = self.get(name)
        if _filter:
            msg = 'Found filter "{}". Rename it to "{}"?'.format(name, newname)
            if ask(msg) == 'Y':
                self.add(newname, raw_filter=_filter['filter'])
                self.delete(name, noconfirm=True)
        else:
            print('Filter "{}" does not exist. Abort now.'.format(name))

