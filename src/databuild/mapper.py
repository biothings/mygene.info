from biothings.utils.common import loadobj
import biothings.databuild.mapper as mapper

class EntrezRetired2Current(mapper.IDMapperBase):

    def __init__(self, db, *args, **kwargs):
        super(EntrezRetired2Current,self).__init__(*args,**kwargs)
        self.db = db

    def load(self):
        if self.map is None:
            # this is a whole dict containing all entrez _id, wether it's a current or retired one.
            # it means most of the data has assoction with same _id as key and as value. It consumes memory
            # but it's a way to know the entrez perimeter (what entrez _ids exist and should be considered
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

    def convert(self,docs,key_to_convert,**kwargs):
        """
        we want to force translation, not defaulting to ensembl if no match
        so, if there's a match, it means ensembl doc can be converted so it means
        we're not interested in keeping this doc since it's already there as a entrez_gene
        Note: it's not really a conversion is this case, it's a filter, we're filtering out
        convertible docs to only keep ensembl docs
        """
        for doc in docs:
            _new = self.translate(doc[key_to_convert],transparent=False)
            if _new:
                continue # already as entrez_gene
            else:
                yield doc # return original
