import sys
import types
import copy
import time
from utils.dataload import dict_attrmerge
from utils.common import timesofar
from utils.mongo import get_src_conn, get_db, get_src

ENTREZ_ROOT = 'entrez_geneinfo'
ENSEMBL_ROOT = 'ensembl_all'

sources = [u'entrez_geneinfo',
 u'entrez_homologene',
 u'entrez_genesummary',
 u'entrez_accession',
 u'entrez_refseq',
 u'entrez_unigene',
 u'entrez_go',
# u'ensembl_all',
 u'entrez_ec',
 u'entrez_retired']


def _merge_ids(src1, src2):
	'''return the union of _ids from two sources.'''
	id_li = []
	id_li1 = src1.find(fields=['_id'])
	id_li2 = src2.find(fields=['_id'])

	src_iter1 = src.find

def _query_to_dict(query_cursor):
    _d = {}
    for doc in query_cursor:
        _d[doc['_id']] = doc
    return _d


def _doc_feeder(coll_or_list, id_list, step=10000, inbatch=False, asdict=False, **query_params):
    '''A generator to feed documents in bulk.
        coll_or_list:   a collection or a list of collections
                          if a collection, one matching doc is returned
                            at a time, otherwise, a list of matching docs
                            from all collections are returned at a time
        id_list:        a list of ids to return
        step:           max number of docs to retrieve in one query
        inbatch:        if True, instead of returning one matching doc or 
                          matching doc_li at a time, return all docs, up to 
                          the number of "step" at a time. 
        asdict:         if True, returns in a form of {'<_id>': doc or doc_li},
                          otherwise, just doc or doc_li.
        query_params:   extra query parameters (e.g. fields) can be passed to "find"
                          query.
        Note that the returned doc or doc_li is guarranteed to be in the same order of 
          input id_list, and also the same size (means the mis-matched ids will returns
          None in the result).
    '''
    if type(coll_or_list) not in (types.ListType, types.TupleType):
        cli = [coll_or_list]
        _single_coll = True
    else:
        cli = coll_or_list
        _single_coll = False

    for i in range(0, len(id_list), step):
        _ids = id_list[i:i+step]
        doc_li = [_query_to_dict(c.find({"_id":{"$in":_ids}}, **query_params)) for c in cli]
        if not inbatch:
            for _id in _ids:
                _doc_li = [doc_d.get(_id, None) for doc_d in doc_li]
                if _single_coll:
                    value =  _doc_li[0]
                else:
                    value = _doc_li
                if asdict:
                    yield {_id: value}
                else:
                    yield value
        else:
            _doc_li = []
            for _id in _ids:
                if _single_coll:
                    _doc_li.append(doc_li[0].get(_id, None))
                else:
                    _doc_li.append([doc_d.get(_id, None) for doc_d in doc_li])
            if asdict:
                yield {_id: _doc_li}
            else:
                yield _doc_li


def merge_root_nodes0():
	s1 = get_src(ENTREZ_ROOT)
	s2 = get_src(ENSEMBL_ROOT)
	id_li = []
	id_li1 = [v['_id'] for v in s1.find(fields=['_id'])]
	id_li2 = [v['_id'] for v in s2.find(fields=['_id'])]
	out_d = {}
	for _id in sorted(set(id_li1) | set(id_li2)):
		_v1 = s1.get_from_id(_id)
		_v2 = s2.get_from_id(_id)
		if _v1 and _v2:
			v = dict_attrmerge([_v1, _v2])
		elif _v1:
			v = _v1
		elif _v2:
			v = _v2
		else:
			raise ValueError, "Should not be here!"

		out_d[_id] = v
	return out_d

def merge_root_nodes():
    s1 = get_src(ENTREZ_ROOT)
    s2 = get_src(ENSEMBL_ROOT)
    id_li = []
    id_li1 = [v['_id'] for v in s1.find(fields=['_id'])]
    id_li2 = [v['_id'] for v in s2.find(fields=['_id'])]
    out_d = {}
    id_all = sorted(set(id_li1) | set(id_li2))
    for doc_li in _doc_feeder((s1, s2), id_all, step=10000):
        _v1, _v2 = doc_li
        if _v1 and _v2:
            v = dict_attrmerge([_v1, _v2])
        elif _v1:
            v = _v1
        elif _v2:
            v = _v2
        else:
            raise ValueError, "Should not be here!"

        out_d[v['_id']] = v
    return out_d

def build(sources, batch=True):
    entrez_root = ENTREZ_ROOT in sources
    ensembl_root = ENSEMBL_ROOT in sources
    print "Preparing root nodes...",
    t0 = time.time()
    if entrez_root and ensembl_root:
    	root_nodes = merge_root_nodes()
    elif entrez_root:
    	root_nodes = list(get_src(ENTREZ_ROOT).find())
    elif ensembl_root:
    	root_nodes = list(get_src(ENSEMBL_ROOT).find())
    else:
    	raise ValueError, "You need at least one source with root nodes."
    print 'Done[%s, %s]' % (len(root_nodes), timesofar(t0))

    print "Merging other sources with root nodes...",
    t0 = time.time()
    _sources = copy.copy(sources)
    if entrez_root:
    	_sources.remove(ENTREZ_ROOT)
    if ensembl_root:
    	_sources.remove(ENSEMBL_ROOT)
    src_collections = [get_src(src) for src in _sources]
    out_d = {}
    if not batch:
        for _id in root_nodes:
            vli = [root_nodes[_id]]
            for sc in src_collections:
                v = sc.get_from_id(_id)
                if v:
                    vli.append(v)
            v_merged = dict_attrmerge(vli)
            out_d[_id] = v_merged
    else:
        for doc_d in _doc_feeder(src_collections, root_nodes.keys(), step=10000, asdict=True):
            _id, vli = doc_d.items()[0]
            vli = [root_nodes[_id]] + [v for v in vli if v]
            v_merged = dict_attrmerge(vli)
            out_d[_id] = v_merged

    print 'Done[%s, %s]' % (len(out_d), timesofar(t0))
    return out_d

def upload(docs, collection):
	'''do the actual upload docs to the db.'''
	print 'Uploading to DB...',
	t0 = time.time()
	if  type(docs) is types.DictType:
		doc_li = docs.values()
	else:
		doc_li = docs

	db = get_db()   #database for merged data
	coll = db[collection]
	for i in range(0, len(doc_li), 10000):
		coll.insert(doc_li[i:i+10000])
	print 'Done[%s]' % timesofar(t0)


def run():
	doc_d = build(sources)
	upload(doc_d, 'genedoc_m1')

def run2():
    from databuild.esbuilder import ESIndexerBase
    esb = ESIndexerBase()
    doc_d = build(sources)
    t0 = time.time()
    esb.build_index(doc_d)
    print 'Done[%s]' % timesofar(t0)




