from biothings.utils.common import loadobj
import biothings.hub.databuild.mapper as mapper

class EntrezRetired2Current(mapper.IDBaseMapper):

    def __init__(self, db_provider, *args, **kwargs):
        super(EntrezRetired2Current,self).__init__(*args,**kwargs)
        self.db_provider = db_provider

    def load(self):
        if self.map is None:
            # this is a whole dict containing all entrez _id, wether it's a current or retired one.
            # it means most of the data has assoction with same _id as key and as value. It consumes memory
            # but it's a way to know the entrez perimeter (what entrez _ids exist and should be considered
            self.map = loadobj(("entrez_gene__geneid_d.pyobj", self.db_provider()), mode='gridfs')

    def process(self,*args,**kwargs):
        raise UserWarning("Don't call me, please")


class Ensembl2Entrez(mapper.IDBaseMapper):
    """
    Mapper to convert ensembl _id to entrez type id.
    """

    def __init__(self, db_provider, retired2current, *args, **kwargs):
        super(Ensembl2Entrez,self).__init__("ensembl2entrez",*args,**kwargs)
        self.db_provider = db_provider
        self.retired2current = retired2current

    def load(self):
        if self.map is None:
            self.retired2current.load()
            self.map = {}
            ensembl2entrez_li = loadobj(("ensembl_gene__2entrezgene_list.pyobj", self.db_provider()), mode='gridfs')
            #filter out those deprecated entrez gene ids
            for ensembl_id,entrez_id in ensembl2entrez_li:
                entrez_id = int(entrez_id)
                if entrez_id in self.retired2current:
                    self.map[ensembl_id] = self.retired2current.translate(entrez_id)


class Ensembl2EntrezRoot(mapper.IDBaseMapper):
    """
    Mapper to select ensembl documents. Those whose _id can be translated
    to entrez are discarded, ensembl-only documents are the only ones kept.
    """

    def __init__(self, ensembl2entrez, *args, **kwargs):
        super(Ensembl2EntrezRoot,self).__init__("ensembl",*args,**kwargs)
        self.ensembl2entrez = ensembl2entrez

    def load(self):
        # this mapper strictly use the same mapping dict as its base class
        if self.map is None:
            self.ensembl2entrez.load()
            self.map = self.ensembl2entrez.map

    def process(self,docs,key_to_convert="_id",**kwargs):
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
