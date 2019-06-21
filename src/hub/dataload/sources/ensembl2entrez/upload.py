import os

from biothings.utils.dataload import tab2dict
import biothings.hub.dataload.uploader as uploader

class Ensembl2EntrezUploader(uploader.BaseSourceUploader):

    name = "ensembl2entrez"

    def load_data(self, data_folder):

        # fn to skip lines with LRG records.'''
        def _not_LRG(ld):
            return not ld[1].startswith("LRG_")

        # load mapping ensembl => entrez from Ensembl
        ens2ent_file = os.path.join(data_folder, 'gene_ensembl__xref_entrezgene__dm.txt')
        self.logger.info("Loading Ensembl-to-Entrez mapping file: %s" % ens2ent_file)
        ens2ent = tab2dict(ens2ent_file, (1, 2), 0, includefn=_not_LRG, alwayslist=True)
        self.logger.info("# mapping Ensembl => Entrez: %s" % len(ens2ent))
        # load mapping entrez => ensembl from Entrez
        ent2ens_file = os.path.join(data_folder, 'gene2ensembl.gz')
        self.logger.info("Loading Entrez-to-Ensembl mapping file: %s" % ent2ens_file)
        ent2ens = tab2dict(ent2ens_file, (1, 2), 0, alwayslist=True)
        self.logger.info("# mapping Entrez => Ensembl: %s" % len(ent2ens))

        # multual mapping
        mapping = {}
        for ensembl_id in ens2ent:
            entrez_ids_from_ensembl = ens2ent[ensembl_id]
            for entrez_id in entrez_ids_from_ensembl:
                if ensembl_id in ent2ens.get(entrez_id,[]):
                    mapping.setdefault(ensembl_id,set()).add(entrez_id)
        self.logger.info("%d mutual mappings found" % len(mapping))
        for ens,ents in mapping.items():
            sents = sorted(list(ents))
            yield {
                    "_id" : "%s-%s" % (ens,",".join(ents)),
                    "multiplicity" : len(sents),
                    "ensembl" : ens,
                    "entrez" : sents,
                    }

        # last doc, sort of metadata
        src_doc = self.src_dump.find_one({"_id":self.main_source}) or {}
        release = src_doc["download"]["release"]
        ens_version,ent_version = release.split(":")
        yield {
                "_id" : "_meta",
                "ensembl" : {
                    "file" : ens2ent_file,
                    "version" : ens_version
                    },
                "entrez" : {
                    "file" : ent2ens_file,
                    "version" : ent_version
                    },
                }

    def post_update_data(self,*args,**kwargs):
        for field in ["ensembl","entrez","multiplicity"]:
            self.logger.info("Indexing '%s'" % field)
            self.collection.create_index(field,background=True)

