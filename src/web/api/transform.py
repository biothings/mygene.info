# -*- coding: utf-8 -*-
from biothings.web.api.es.transform import ESResultTransformer

class ESResultTransformer(ESResultTransformer):
    # Add app specific result transformations
    def _clean_annotation_POST_response(self, bid_list, res, single_hit=False):
        return self._clean_common_POST_response(_list=bid_list, res=res, single_hit=single_hit, score=True)

    def clean_annotation_GET_response(self, res):
        return self._clean_annotation_GET_response(res, score=True)
