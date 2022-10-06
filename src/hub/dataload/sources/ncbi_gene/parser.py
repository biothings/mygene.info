import os
from biothings.utils.dataload import dict_convert, tab2dict_iter
from biothings.utils.common import open_anyfile

try:
    from ..entrez.parser import EntrezParserBase
except (ValueError, ImportError):
    # capture "ValueError: Attempted relative import beyond top-level package"
    # or other ImportError
    from hub.dataload.sources.entrez.parser import EntrezParserBase


class GeneSummaryParser(EntrezParserBase):
    '''Parser for gene2summary_all.txt.xz, adding "summary" field in gene doc'''

    # TODO testing only need to change file name
    DATAFILE = 'gene2summary_sus.txt.xz'

    def load(self, aslist=False):

        doc_li = []
        with open_anyfile(self.datafile) as df:
            for line in df:
                geneid, summary = line.strip().split('\t')
                doc_li.append(dict(_id=geneid, summary=str(summary)))


        if aslist:
            return doc_li
        else:
            gene_d = dict([(d['_id'], d) for d in doc_li])
            return gene_d