from biothings.utils.common import loadobj
import biothings.databuild.mapper as mapper

class EntrezRetired2Current(mapper.IDMapperBase):

    def __init__(self, db, *args, **kwargs):
        super(EntrezRetired2Current,self).__init__(*args,**kwargs)
        self.db = db

    def load(self):
        if self.map is None:
            self.map = loadobj(("entrez_gene__geneid_d.pyobj", self.db), mode='gridfs')


class Ensembl2Entrez(mapper.IDMapperBase):

    def __init__(self, name, db, retired2current, *args, **kwargs):
        super(Ensembl2Entrez,self).__init__(name,*args,**kwargs)
        self.db = db
        self.retired2current = retired2current

    def load(self):
        if self.map is None:
            self.retired2current.load()
            self.map = {}
            ensembl2entrez_li = loadobj(("ensembl_gene__2entrezgene_list.pyobj", self.db), mode='gridfs')
            #filter out those deprecated entrez gene ids
            for ensembl_id,entrez_id in ensembl2entrez_li:
                entrez_id = int(entrez_id)
                if entrez_id in self.retired2current:
                    self.map[ensembl_id] = self.retired2current.translate(entrez_id)


