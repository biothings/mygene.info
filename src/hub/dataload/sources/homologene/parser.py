import os.path
from config import TAXONOMY
from biothings.utils.common import file_newer, loadobj, dump
from biothings.utils.dataload import tab2dict

from ..entrez.parser import EntrezParserBase, get_geneid_d


class HomologeneParser(EntrezParserBase):
    '''Parser for NCBI homologenes.data file.'''
    DATAFILE = 'homologene.data'

    def _sorted_homologenes(self, homologenes):
        '''sort list of homologenes [(taxid, geneid),...] based on the order
            defined in species_li.
        '''
        d = {}
        for i, species in enumerate(list(TAXONOMY.keys())):
            d[TAXONOMY[species]["tax_id"]] = i
        gene_li = [(d.get(taxid, taxid), taxid, geneid)
                   for taxid, geneid in homologenes]
        return [g[1:] for g in sorted(gene_li)]

    def load(self, aslist=False):
        '''
        loading ncbi "homologene.data" file
        adding "homologene" field in gene doc
        '''
        from biothings.utils.hub_db import get_src_dump
        homo_d = tab2dict(self.datafile,(2,1),0,header=0)
        entrez_doc = get_src_dump().find_one({"_id":"entrez"}) or {}
        entrez_dir = entrez_doc.get("data_folder")
        assert entrez_dir, "Can't find Entez data directory"
        DATAFILE = os.path.join(entrez_dir, 'gene_history.gz')
        assert os.path.exists(DATAFILE), "gene_history.gz is missing (entrez_dir: %s)" % entrez_dir
        retired2gene = tab2dict(DATAFILE, (1, 2), 1, alwayslist=0,includefn=lambda ld: ld[1] != '-')
        for id in list(homo_d.keys()):
            homo_d[retired2gene.get(id,id)] = homo_d[id]

        with open(self.datafile) as df:
            homologene_d = {}
            doc_li = []
            print()
            geneid_d = get_geneid_d(entrez_dir, self.species_li,load_cache=False,save_cache=False,only_for=homo_d)

            for line in df:
                ld = line.strip().split('\t')
                hm_id, tax_id, geneid = [int(x) for x in ld[:3]]
                if (self.taxid_set is None or tax_id in self.taxid_set) and geneid in geneid_d:
                    # for selected species only
                    # and also ignore those geneid does not match any
                    # existing gene doc
                    # in case of orignal geneid is retired, replaced with the
                    # new one, if available.
                    geneid = geneid_d[geneid]
                    genes = homologene_d.get(hm_id, [])
                    genes.append((tax_id, geneid))
                    homologene_d[hm_id] = genes

                    doc_li.append(dict(_id=str(geneid), taxid=tax_id,
                                       homologene={'id': hm_id}))

            for i, gdoc in enumerate(doc_li):
                gdoc['homologene']['genes'] = self._sorted_homologenes(
                    set(homologene_d[gdoc['homologene']['id']]))
                doc_li[i] = gdoc

        if aslist:
            return doc_li
        else:
            gene_d = dict([(d['_id'], d) for d in doc_li])
            return gene_d

