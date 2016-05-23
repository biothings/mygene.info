from __future__ import print_function
import time
from pymongo import MongoClient
from config import (DATA_SRC_SERVER, DATA_SRC_PORT, DATA_SRC_DATABASE,
                    DATA_SRC_MASTER_COLLECTION, DATA_SRC_DUMP_COLLECTION,
                    DATA_SRC_BUILD_COLLECTION,
                    DATA_SERVER_USERNAME, DATA_SERVER_PASSWORD,
                    DATA_TARGET_SERVER, DATA_TARGET_PORT, DATA_TARGET_DATABASE,
                    DATA_TARGET_MASTER_COLLECTION)
from biothings.utils.common import timesofar


class Connection(MongoClient):
    """
    This class mimicks / is a mock for mongokit.Connection class,
    used to keep used interface (registering document model for instance)
    """
    def __init__(self, *args, **kwargs):
        super(Connection,self).__init__(*args,**kwargs)
        self._registered_documents = {}
    def register(self, obj):
        self._registered_documents[obj.__name__] = obj
    def __getattr__(self,key):
        if key in self._registered_documents:
            document = self._registered_documents[key]
            return document
        else:
            try:
                return self[key]
            except Exception:
                raise AttributeError(key)

def get_conn(server, port):
    # TODO: split username/passwd for src/target server
    if DATA_SERVER_USERNAME and DATA_SERVER_PASSWORD:
        uri = "mongodb://{}:{}@{}:{}".format(DATA_SERVER_USERNAME,
                                             DATA_SERVER_PASSWORD,
                                             server, port)
    else:
        uri = "mongodb://{}:{}".format(server, port)
    conn = Connection(uri)
    return conn


def get_src_conn():
    return get_conn(DATA_SRC_SERVER, DATA_SRC_PORT)


def get_src_db(conn=None):
    conn = conn or get_src_conn()
    return conn[DATA_SRC_DATABASE]


def get_src_master(conn=None):
    conn = conn or get_src_conn()
    return conn[DATA_SRC_DATABASE][DATA_SRC_MASTER_COLLECTION]


def get_src_dump(conn=None):
    conn = conn or get_src_conn()
    return conn[DATA_SRC_DATABASE][DATA_SRC_DUMP_COLLECTION]


def get_src_build(conn=None):
    conn = conn or get_src_conn()
    return conn[DATA_SRC_DATABASE][DATA_SRC_BUILD_COLLECTION]


def get_target_conn():
    return get_conn(DATA_TARGET_SERVER, DATA_TARGET_PORT)


def get_target_db(conn=None):
    conn = conn or get_target_conn()
    return conn[DATA_TARGET_DATABASE]


def get_target_master(conn=None):
    conn = conn or get_target_conn()
    return conn[DATA_TARGET_DATABASE][DATA_TARGET_MASTER_COLLECTION]


def doc_feeder0(collection, step=1000, s=None, e=None, inbatch=False):
    '''A iterator for returning docs in a collection, with batch query.'''
    n = collection.count()
    s = s or 1
    e = e or n
    print('Found %d documents in database "%s".' % (n, collection.name))
    for i in range(s - 1, e + 1, step):
        print("Processing %d-%d documents..." % (i + 1, i + step), end='')
        t0 = time.time()
        res = collection.find(skip=i, limit=step, timeout=False)
        if inbatch:
            yield res
        else:
            for doc in res:
                yield doc
        print('Done.[%s]' % timesofar(t0))

# TODO: use biothjngs.utils.mongo.doc_feeder()
def doc_feeder(collection, step=1000, s=None, e=None, inbatch=False, query=None, batch_callback=None, fields=None):
    '''A iterator for returning docs in a collection, with batch query.
       additional filter query can be passed via "query", e.g.,
       doc_feeder(collection, query={'taxid': {'$in': [9606, 10090, 10116]}})
       batch_callback is a callback function as fn(cnt, t), called after every batch
       fields is optional parameter passed to find to restrict fields to return.
    '''
    cur = collection.find(query, no_cursor_timeout=False, projection=fields)
    n = cur.count()
    s = s or 0
    e = e or n
    print('Retrieving %d documents from database "%s".' % (n, collection.name))
    t0 = time.time()
    if inbatch:
        doc_li = []
    cnt = 0
    t1 = time.time()
    try:
        if s:
            cur.skip(s)
            cnt = s
            print("Skipping %d documents." % s)
        if e:
            cur.limit(e - (s or 0))
        cur.batch_size(step)
        print("Processing %d-%d documents..." % (cnt + 1, min(cnt + step, e)), end='')
        for doc in cur:
            if inbatch:
                doc_li.append(doc)
            else:
                yield doc
            cnt += 1
            if cnt % step == 0:
                if inbatch:
                    yield doc_li
                    doc_li = []
                print('Done.[%.1f%%,%s]' % (cnt * 100. / n, timesofar(t1)))
                if batch_callback:
                    batch_callback(cnt, time.time()-t1)
                if cnt < e:
                    t1 = time.time()
                    print("Processing %d-%d documents..." % (cnt + 1, min(cnt + step, e)), end='')
        if inbatch and doc_li:
            #Important: need to yield the last batch here
            yield doc_li

        #print 'Done.[%s]' % timesofar(t1)
        print('Done.[%.1f%%,%s]' % (cnt * 100. / n, timesofar(t1)))
        print("=" * 20)
        print('Finished.[total time: %s]' % timesofar(t0))
    finally:
        cur.close()


def src_clean_archives(keep_last=1, src=None, verbose=True, noconfirm=False):
    '''clean up archive collections in src db, only keep last <kepp_last>
       number of archive.
    '''
    from utils.dataload import list2dict
    from biothings.utils.common import ask

    src = src or get_src_db()

    archive_li = sorted([(coll.split('_archive_')[0], coll) for coll in src.collection_names()
                         if coll.find('archive') != -1])
    archive_d = list2dict(archive_li, 0, alwayslist=1)
    coll_to_remove = []
    for k, v in archive_d.items():
        print(k, end='')
        #check current collection exists
        if src[k].count() > 0:
            cnt = 0
            for coll in sorted(v)[:-keep_last]:
                coll_to_remove.append(coll)
                cnt += 1
            print("\t\t%s archived collections marked to remove." % cnt)
        else:
            print('skipped. Missing current "%s" collection!' % k)
    if len(coll_to_remove) > 0:
        print("%d archived collections will be removed." % len(coll_to_remove))
        if verbose:
            for coll in coll_to_remove:
                print('\t', coll)
        if noconfirm or ask("Continue?") == 'Y':
            for coll in coll_to_remove:
                src[coll].drop()
            print("Done.[%s collections removed]" % len(coll_to_remove))
        else:
            print("Aborted.")
    else:
        print("Nothing needs to be removed.")


def target_clean_collections(keep_last=2, target=None, verbose=True, noconfirm=False):
    '''clean up collections in target db, only keep last <keep_last> number of collections.'''
    import re
    from biothings.utils.common import ask

    target = target or get_target_db()
    coll_list = target.collection_names()

    for prefix in ('genedoc_mygene', 'genedoc_mygene_allspecies'):
        pat = prefix + '_(\d{8})_\w{8}'
        _li = []
        for coll_name in coll_list:
            mat = re.match(pat, coll_name)
            if mat:
                _li.append((mat.group(1), coll_name))
        _li.sort()   # older collection appears first
        coll_to_remove = [x[1] for x in _li[:-keep_last]]   # keep last # of newer collections
        if len(coll_to_remove) > 0:
            print('{} "{}*" collection(s) will be removed.'.format(len(coll_to_remove), prefix))
            if verbose:
                for coll in coll_to_remove:
                    print('\t', coll)
            if noconfirm or ask("Continue?") == 'Y':
                for coll in coll_to_remove:
                    target[coll].drop()
                print("Done.[%s collection(s) removed]" % len(coll_to_remove))
            else:
                print("Aborted.")
        else:
            print("Nothing needs to be removed.")


def backup_src_configs():
    import json
    import os
    from utils.common import send_s3_file, get_timestamp, DateTimeJSONEncoder

    db = get_src_db()
    for cfg in ['src_dump', 'src_master', 'src_build']:
        xli = list(db[cfg].find())
        bakfile = '/tmp/{}_{}.json'.format(cfg, get_timestamp())
        bak_f = file(bakfile, 'w')
        json.dump(xli, bak_f, cls=DateTimeJSONEncoder, indent=2)
        bak_f.close()
        bakfile_key = 'genedoc_src_config_bk/' + os.path.split(bakfile)[1]
        print('Saving to S3: "{}"... '.format(bakfile_key), end='')
        send_s3_file(bakfile, bakfile_key, overwrite=True)
        os.remove(bakfile)
        print('Done.')
