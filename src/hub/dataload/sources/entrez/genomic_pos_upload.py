'''
Populates MICROBE gene entries with genomic position data from NCBI's gene2refseq,
limited to the bacterial reference genome taxids built by the ref_microbe_taxids
(refmicrobe) source.
'''

import os.path
from biothings.utils.common import loadobj
from biothings.utils.dataload import tabfile_feeder
import biothings.hub.dataload.uploader as uploader
from biothings.utils.hub_db import get_src_dump

class EntrezGenomicPosUploader(uploader.MergerSourceUploader):

    name = "entrez_genomic_pos"
    main_source = "entrez"

    def load_data(self, data_folder):
        """
        Loads gene data from NCBI's gene2refseq.gz file.
        Keeps genomic position data for genes whose taxid is in the list built by
        the ref_microbe_taxids (refmicrobe) source.
        :return:
        """

        refsrc = get_src_dump().find_one({"_id":"ref_microbe_taxids"})
        assert refsrc, "ref_microbe_taxids dump not found"
        taxids_file = os.path.join(refsrc["download"]["data_folder"], "ref_microbe_taxids.pyobj")
        datafile = os.path.join(data_folder, 'gene2refseq.gz')

        taxids = loadobj(taxids_file)
        taxid_set = set(taxids)

        def _includefn(ld):
            # match taxid from taxid_set, skip rows without a genomic position
            return ld[0] in taxid_set and ld[9] != '-' and ld[10] != '-'

        cols_included = [0, 1, 7, 9, 10, 11]  # 0-based col idx
        # stream rows rather than loading every matching row into memory (tab2list)
        gene2genomic_pos_li = ([ld[i] for i in cols_included]
                               for ld in tabfile_feeder(datafile, header=1, includefn=_includefn))
        count = 0
        last_id = None
        for gene in gene2genomic_pos_li:
            count += 1
            strand = 1 if gene[5] == '+' else -1
            _id = gene[1]

            mgi_dict = {
                '_id': _id,
                'genomic_pos': {
                    'entrezgene': _id,
                    'start': int(gene[3]),
                    'end': int(gene[4]),
                    'chr': gene[2],
                    'strand': strand
                }
            }
            if _id != last_id:
                # rows with dup _id will be skipped
                yield mgi_dict
            last_id = _id

    @classmethod
    def get_mapping(klass):
        mapping = {
            "genomic_pos": {
                "dynamic": False,
                "type": "nested",
                "properties": {
                    "chr": {
                        "type": "keyword",
                        "normalizer" : "keyword_lowercase_normalizer",
                        },
                    "start": {"type": "long"},
                    "end": {"type": "long"},
                    "strand": {
                        "type": "byte",
                        "index": False,
                    },
                },
            },
        }

        return mapping
