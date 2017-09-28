from biothings.utils.dataload import dict_convert, tab2dict_iter

from ..entrez.parser import EntrezParserBase

class Gene2GeneRifParser(EntrezParserBase):
    '''
    '''
    DATAFILE = 'generifs_basic.gz'

    def _cvt_pubmed(self, pubmed_str):
        """input is a string of one or multiple pubmed ids, sep by comma"""
        _li = [int(x) for x in pubmed_str.split(',')]
        if len(_li) == 1:
            return _li[0]
        else:
            return _li

    def load(self):
        cnt = 0
        for datadict in tab2dict_iter(self.datafile, (1, 2, 4), 0, alwayslist=1):
            datadict = dict_convert(datadict, valuefn=lambda v: {
                            'generif': [dict(pubmed=self._cvt_pubmed(x[0]), text=x[1]) for x in v]})

            for id,doc in datadict.items():
                cnt += 1
                doc['_id'] = id
                yield doc
