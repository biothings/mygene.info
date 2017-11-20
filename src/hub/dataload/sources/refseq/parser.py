import os.path
import datetime
from biothings.utils.common import file_newer, loadobj, dump
from biothings.utils.dataload import tab2dict, tab2list, value_convert, \
                            normalized_value, dict_convert, dict_to_list, \
                            tab2dict_iter

from ..entrez.parser import EntrezParserBase


class GeneSummaryParser(EntrezParserBase):
    '''Parser for gene2summary_all.txt, adding "summary" field in gene doc'''
    DATAFILE = 'gene2summary_all.txt'

    def load(self, aslist=False):
        with open(self.datafile) as df:
            geneid_set = set()
            doc_li = []
            for line in df:
                geneid, summary = line.strip().split('\t')
                if geneid not in geneid_set:
                    doc_li.append(dict(_id=geneid, summary=str(summary)))
                    geneid_set.add(geneid)

        if aslist:
            return doc_li
        else:
            gene_d = dict([(d['_id'], d) for d in doc_li])
            return gene_d


class Gene2ECParser(EntrezParserBase):
    '''
    loading gene2ec data, adding "ec" field in gene doc

    Sample lines for input file:
        24159   2.3.3.8
        24161   3.1.3.2,3.1.3.48
    '''
    DATAFILE = 'gene2ec_all.txt'

    def load(self, aslist=False):
        with open(self.datafile) as df:
            geneid_set = set()
            doc_li = []
            for line in df:
                geneid, ec = line.strip().split('\t')
                if ec.find(',') != -1:
                    # there are multiple EC numbers
                    ec = [str(x) for x in ec.split(',')]
                else:
                    ec = str(ec)
                if geneid not in geneid_set:
                    doc_li.append(dict(_id=geneid, ec=ec))
                    geneid_set.add(geneid)

        if aslist:
            return doc_li
        else:
            gene_d = dict([(d['_id'], d) for d in doc_li])
            return gene_d


class Gene2GeneRifParser(EntrezParserBase):
    '''
    '''
    DATAFILE = 'generif/generifs_basic.gz'

    def _cvt_pubmed(self, pubmed_str):
        """input is a string of one or multiple pubmed ids, sep by comma"""
        _li = [int(x) for x in pubmed_str.split(',')]
        if len(_li) == 1:
            return _li[0]
        else:
            return _li

    def load(self):
        cnt = 0
        for datadict in tab2dict_iter(self.datafile, (1, 2, 4), 0, alwayslist=1, encoding="latin1"):
            datadict = dict_convert(datadict, valuefn=lambda v: {
                            'generif': [dict(pubmed=self._cvt_pubmed(x[0]), text=x[1]) for x in v]})

            for id,doc in datadict.items():
                cnt += 1
                doc['_id'] = id
                yield doc
        #gene2generif = tab2dict(self.datafile, (1, 2, 4), 0, alwayslist=1)
        #gene2generif = dict_convert(gene2generif, valuefn=lambda v: {
        #    'generif': [dict(pubmed=self._cvt_pubmed(x[0]), text=x[1]) for x in v]})
