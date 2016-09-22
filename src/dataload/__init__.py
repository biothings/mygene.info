import time, datetime
import importlib

from biothings.utils.common import timesofar, dump2gridfs
import biothings.dataload.uploader as uploader


__sources_dict__ = {
    'entrez': [
        'entrez.entrez_gene',
        'entrez.entrez_homologene',
        'entrez.entrez_genesummary',
        'entrez.entrez_accession',
        'entrez.entrez_refseq',
        'entrez.entrez_unigene',
        'entrez.entrez_go',
        'entrez.entrez_ec',
        'entrez.entrez_retired',
        'entrez.entrez_generif',
        'entrez.entrez_genomic_pos',
    ],
    'ensembl': [
        'ensembl.ensembl_gene',
        'ensembl.ensembl_acc',
        'ensembl.ensembl_genomic_pos',
        'ensembl.ensembl_prosite',
        'ensembl.ensembl_interpro',
        'ensembl.ensembl_pfam'
    ],
    'uniprot': [
        'uniprot',
        'uniprot.uniprot_pdb',
        # 'uniprot.uniprot_ipi',   # IPI is now discontinued, last update is still in the db, but won't be updated.
        'uniprot.uniprot_pir'
    ],
    'pharmgkb': ['pharmgkb'],
    'reporter': ['reporter'],
    'ucsc': ['ucsc.ucsc_exons'],
    'exac': ['exac.broadinstitute_exac'],
    'cpdb': ['cpdb'],
    'reagent': ['reagent'],
}



class MyGeneSourceUploader(uploader.SourceUploader):

    def register_sources(self):
        for src in self.__sources__:
            src_m = importlib.import_module('dataload.sources.' + src)
            metadata = src_m.__metadata__
            name = src + '_doc'
            metadata['load_data'] = src_m.load_data
            metadata['get_mapping'] = src_m.get_mapping
            metadata['conn'] = self.conn
            if metadata.get('ENTREZ_GENEDOC_ROOT', False):
                metadata['get_geneid_d'] = src_m.get_geneid_d
            if metadata.get('ENSEMBL_GENEDOC_ROOT', False):
                metadata['get_mapping_to_entrez'] = src_m.get_mapping_to_entrez
            src_cls = type(name, (GeneDocSource,), metadata)
	        # manually propagate db attr
            src_cls.db = self.conn[src_cls.__database__]
            self.doc_register[name] = src_cls
            self.conn.register(src_cls)

class GeneDocSource(uploader.DocSource):

    def post_update_data(self):
        if getattr(self, 'ENTREZ_GENEDOC_ROOT', False):
            print('Uploading "geneid_d" to GridFS...', end='')
            t0 = time.time()
            geneid_d = self.get_geneid_d()
            dump2gridfs(geneid_d, self.__collection__ + '__geneid_d.pyobj', self.db)
            print('Done[%s]' % timesofar(t0))
        if getattr(self, 'ENSEMBL_GENEDOC_ROOT', False):
            print('Uploading "mapping2entrezgene" to GridFS...', end='')
            t0 = time.time()
            x2entrezgene_list = self.get_mapping_to_entrez()
            dump2gridfs(x2entrezgene_list, self.__collection__ + '__2entrezgene_list.pyobj', self.db)
            print('Done[%s]' % timesofar(t0))

    def generate_doc_src_master(self):
        _doc = {"_id": str(self.__collection__),
                "name": str(self.__collection__),
                "timestamp": datetime.datetime.now()}
        for attr in ['ENTREZ_GENEDOC_ROOT', 'ENSEMBL_GENEDOC_ROOT', 'id_type']:
            if hasattr(self, attr):
                _doc[attr] = getattr(self, attr)
        if hasattr(self, 'get_mapping'):
            _doc['mapping'] = getattr(self, 'get_mapping')()

        return _doc

