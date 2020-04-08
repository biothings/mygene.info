
import pytest

from biothings.tests.web import BiothingsTestCase


class TestControlKeywords(BiothingsTestCase):

    def test_501_format_msgpack(self):

        # format and out_format are an aliases
        # effective for both annotation and query
        # effective for both GET and POST requests

        # former request syntax is msgpack=true

        res = self.request('gene/1017').json()
        res2 = msgpack_ok(self.request("gene/1017?format=msgpack").content)
        assert res, res2

    def test_502_format_msgpack(self):
        res = self.request('query/?q=cdk').json()
        res2 = msgpack_ok(self.request("query/?q=cdk&format=msgpack").content)
        assert res, res2

    def test_503_format_msgpack(self):
        res = self.request('metadata').json()
        res2 = msgpack_ok(self.request("metadata?format=msgpack").content)
        assert res, res2

    def test_511_raw(self):
        raw1 = self.request('gene/1017?raw=1').json()
        rawtrue = self.request('gene/1017?raw=true').json()
        raw0 = self.request('gene/1017?raw=0').json()
        rawfalse = self.request('gene/1017?raw=false').json()
        assert sorted(raw1) == sorted(rawtrue)
        raw0.pop("_score", None)
        rawfalse.pop("_score", None)
        assert raw0 == rawfalse
        assert "_shards" in raw1
        assert "_shards" not in raw0
        assert "timed_out" in raw1
        assert "timed_out" not in raw0

    def test_512_raw(self):
        # query
        raw1 = self.request("query?q=ccnk&raw=1&size=3").json()
        rawtrue = self.request("query?q=ccnk&raw=true&size=3").json()
        raw0 = self.request("query?q=ccnk&raw=0&size=3").json()
        rawfalse = self.request("query?q=ccnk&raw=false&size=3").json()
        # this may vary so remove in comparison
        for res in [raw1, rawtrue, raw0, rawfalse]:
            del res["took"]
        # score should be the same. approx... so remove
        for res in [raw1, rawtrue]:
            for hit in res["hits"]["hits"]:
                del hit["_score"]
            del res["hits"]["max_score"]
        for res in [raw0, rawfalse]:
            for hit in res["hits"]:
                del hit["_score"]
            del res["max_score"]
        assert raw1 == rawtrue
        assert raw0 == rawfalse
        assert "_shards" in raw1
        assert "_shards" not in raw0

    def test_521_fields(self):
        # Aliases: _source, fields, filter
        # Endpoints: annotation, query
        # Methods: GET, POST

        res = self.request('gene/1017?fields=symbol,name,entrezgene').json()
        assert set(res) == set(['_id', '_version', 'symbol', 'name', 'entrezgene'])

    def test_522_fields(self):
        res = self.request('gene/1017?filter=symbol,go.MF').json()
        assert set(res) == set(['_id', '_version', 'symbol', 'go'])
        assert "MF" in res["go"]

    def test_531_dotfield(self):
        # query service
        # default dotfield=0
        rdefault = self.request("query?q=ccnk&fields=refseq.rna&size=3").json()
        # force no dotfield
        rfalse = self.request("query?q=ccnk&fields=refseq.rna&dotfield=false&size=3").json()
        # force dotfield
        rtrue = self.request("query?q=ccnk&fields=refseq.rna&dotfield=true&size=3").json()
        # check defaults and bool params
        # TODO: put this in json_ok as post-process filter ?
        for res in [rdefault, rfalse, rtrue]:
            for hit in res["hits"]:
                del hit["_score"]
        assert rdefault["hits"] == rfalse["hits"]
        # check struct
        assert "refseq.rna" in rtrue["hits"][0].keys()
        assert "refseq" in rdefault["hits"][0].keys()
        assert "rna" in rdefault["hits"][0]["refseq"].keys()
        # TODO: no fields but dotfield => dotfield results
        # TODO: fields with dot but no dotfield => dotfield results

    def test_532_dotfield(self):
        # /gene service
        rdefault = self.request("gene/1017?filter=symbol,go.MF").json()
        rtrue = self.request("gene/1017?filter=symbol,go.MF&dotfield=true").json()
        rfalse = self.request("gene/1017?filter=symbol,go.MF&dotfield=false").json()
        # sharding makes scoring slightly variable
        rdefault.pop("_version")
        rfalse.pop("_version")
        assert rdefault == rfalse
        assert "go.MF.term" in rtrue.keys()
        assert "go" in rdefault.keys()
        assert "MF" in rdefault["go"].keys()

    def test_541_list_null(self):
        ##
        # TODO test.test2 syntax is non deterministic, does not make sense to inject
        ##
        res = self.request('gene/1017?always_list=entrezgene&allow_null=test.test2').json()
        assert 'entrezgene' in res
        assert isinstance(res['entrezgene'], list)
        assert 'test' in res
        assert 'test2' in res['test']
        assert res['test']['test2'] is None


def msgpack_ok(packed_bytes, checkerror=True):
    ''' Load msgpack into a dict '''
    try:
        import msgpack
    except ImportError:
        pytest.skip('Msgpack is not installed.')
    try:
        dic = msgpack.unpackb(packed_bytes)
    except BaseException:  # pylint: disable=bare-except
        assert False, 'Not a valid Msgpack binary.'
    if checkerror:
        assert not (isinstance(dic, dict)
                    and 'error' in dic), truncate(str(dic), 100)
    return dic


def truncate(string, limit):
    ''' Truncate a long string with a trailing ellipsis '''
    if len(string) <= limit:
        return string
    return string[:limit] + '...'
