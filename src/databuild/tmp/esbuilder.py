import time
from pyes import ES, StringQuery
from pyes.exceptions import (IndexMissingException, ElasticSearchException,
							 NotFoundException)
from config import ES_HOST, ES_INDEX_NAME
from utils import ask, timesofar


class ESIndexerBase(object):
    ES_HOST = ES_HOST
    ES_INDEX_NAME = ES_INDEX_NAME
    ES_INDEX_TYPE = 'gene'

    def __init__(self):
        self.conn = ES(self.ES_HOST, default_indexes=[self.ES_INDEX_NAME],
        	           timeout=10.0)
        self.step = 10000

    def create_index(self):
        try:
            print self.conn.open_index(self.ES_INDEX_NAME)
        except IndexMissingException:
            print self.conn.create_index(self.ES_INDEX_NAME)

    def delete_index_type(self, index_type):
        '''Delete all indexes for a given index_type.'''
        index_name = self.ES_INDEX_NAME
#        index_type = self.ES_INDEX_TYPE
        #Check if index_type exists
        mapping = self.conn.get_mapping(index_type, index_name)
        if index_name not in mapping or index_type not in mapping[index_name]:
            print 'Error: index type "%s" does not exist in index "%s".' % (index_type, index_name)
            return
        path = '/%s/%s' % (index_name, index_type)
        if ask('Confirm to delete all data under "%s":' % path) == 'Y':
            return self.conn.delete_mapping(index_name, index_type)

    def index(self, doc, index_type, id=None):
        '''add a doc to the index. If id is not None, the existing doc will be
           updated.
        '''
#        index_type = self.ES_INDEX_TYPE
        return self.conn.index(doc, self.ES_INDEX_NAME, index_type, id=id)

    def delete_index(self, index_type, id):
        '''delete a doc from the index based on passed id.'''
#        index_type = self.ES_INDEX_TYPE
        return self.conn.delete(self.ES_INDEX_NAME, index_type, id)

    def optimize(self):
        return self.conn.optimize(self.ES_INDEX_NAME, wait_for_merge=True)

    def get_field_mapping(self):
        import dataload
        reload(dataload)
        dataload.register_sources()
        return dataload.get_mapping()

    def build_index(self, doc_d, update_mapping=False, bulk=True):
        index_name = self.ES_INDEX_NAME
        index_type = self.ES_INDEX_TYPE

        #Test if index exists
        try:
            print "Opening index...", self.conn.open_index(index_name)
        except NotFoundException:
            print 'Error: index "%s" does not exist. Create it first.' % index_name
            return -1

        try:
            cur_mapping = self.conn.get_mapping(index_type, index_name)
            empty_mapping = False
        except ElasticSearchException:
            #if no existing mapping available for index_type
            #force update_mapping to True
            empty_mapping = True
            update_mapping = True

#        empty_mapping = not cur_mapping[index_name].get(index_type, {})
#        if empty_mapping:
#            #if no existing mapping available for index_type
#            #force update_mapping to True
#            update_mapping = True

        if update_mapping:
            print "Updating mapping...",
            if not empty_mapping:
                print "\n\tRemoving existing mapping...",
                print self.conn.delete_mapping(index_name, index_type)
            _mapping = self.get_field_mapping()
            print self.conn.put_mapping(index_type,
                                   _mapping,
                                   [index_name])
        print "Building index..."
        t0 = time.time()
        for doc_id, doc in doc_d.items():
            self.conn.index(doc, index_name, index_type, doc_id, bulk=bulk)
        print self.conn.flush()
        print self.conn.refresh()
        print "Done[%s]" % timesofar(t0)

    def query(self, qs, fields='symbol,name', **kwargs):
        _q = StringQuery(qs)
        res = self.conn.search(_q, fields=fields, **kwargs)
        return res