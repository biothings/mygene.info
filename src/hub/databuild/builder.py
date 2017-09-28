
import biothings.hub.databuild.builder as builder

class MyGeneDataBuilder(builder.DataBuilder):

    def generate_document_query(self, src_name):
        """Root documents are created according to species list"""
        _query = None
        if src_name in self.get_root_document_sources():
            if "species" in self.build_config:
                _query = {'taxid': {'$in': list(map(int,self.build_config['species']))}}
            elif "species_to_exclude" in self.build_config:
                _query = {'taxid': {'$nin': list(map(int,self.build_config['species_to_exclude']))}}
            else:
                _query = None
        if _query:
            self.logger.debug("Source '%s' requires custom query: '%s'" % (src_name,_query))
        return _query

    def document_cleaner(self,src_name,*args,**kwargs):
        # only root sources document can keep their taxid
        if src_name in self.get_root_document_sources():
            return None
        else:
            return cleaner


def cleaner(doc):
    doc.pop('taxid', None)
    return doc
