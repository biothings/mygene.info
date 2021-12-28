# Copyright [2010-2017] [Chunlei Wu]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os.path
import glob
import time
import logging
from Bio import SeqIO
from Bio.SeqFeature import FeatureLocation

from biothings.utils.common import SubStr, anyfile

class GBFFParser():
    def __init__(self, infile):
        self.infile = infile
        self.in_f = anyfile(self.infile)

    def parse(self):
        out_li = []
        for rec in SeqIO.parse(self.in_f, 'genbank'):
            geneid = self.get_geneid(rec)
            if geneid:
                summary = self.get_summary(rec)
                ec_list = self.get_ec_numbers(rec)
                cds = self.get_cds(rec)
                ccds = cds[0]
                location = cds[1]
                refseq = rec.id
                if summary or ec_list or ccds:
                    out_li.append((geneid, summary, ec_list, ccds, location, refseq))
        return out_li

    def get_geneid(self, rec):
        '''Return geneid as integer, None if not found.'''
        geneid = None
        gene_feature = [x for x in rec.features if x.type == 'gene']
        # NCBI has now fixed this issue (https://twitter.com/kdpru/status/474673626730741761)
        # if len(gene_feature) == 0 and rec.id == 'NR_001526.1':
        #     print "Known error for NR_001526.1. Fixed."
        #     return '252949'         # a temp fix for this wrong rec from NCBI
        assert len(gene_feature) == 1, '#: {}, id: {}'.format(len(gene_feature), rec.id)
        gene_feature = gene_feature[0]
        db_xref = gene_feature.qualifiers.get('db_xref', None)
        if db_xref:
            x = [x for x in db_xref if x.startswith('GeneID:')]
            if len(x) == 1:
                geneid = int(SubStr(x[0], 'GeneID:'))
        return geneid

    def get_summary(self, rec):
        '''Return summary string if available, return '' otherwise.'''
        summary = ''
        comment = rec.annotations.get('comment', None)
        if comment:
            if comment.find('Summary:') != -1:
                summary = SubStr(comment, 'Summary: ',).replace('\n', ' ')
                for end_str in [# '[provided by RefSeq].',
                                #'[provided by ',
                                #'[supplied by ',
                                '##',
                                # '[RGD',
                                'COMPLETENESS:',
                                'Sequence Note:',
                                'Transcript Variant:',
                                'CCDS Note:',
                                'Publication Note:',
                                ' '*10]:
                    if summary.find(end_str) != -1:
                        summary = SubStr(summary, end_string=end_str)
                summary = summary.strip()
        return summary

    def get_ec_numbers(self, rec):
        '''Return a list of EC numbers if available, return [] if not found.'''
        ec_list = []
        cds_feature = [x for x in rec.features if x.type == 'CDS']
        if cds_feature:
            assert len(cds_feature) == 1, self.get_geneid(rec)
            cds_feature = cds_feature[0]
            ec_list = cds_feature.qualifiers.get('EC_number', [])
            assert isinstance(ec_list, list)
#            ec_list = [SubStr(x, 'EC_number="', '"') for x in ec_qualifiers]
        return ec_list

    def get_cds(self, rec):
        ccds = None
        location = None
        cds_feature = [x for x in rec.features if x.type == 'CDS']
        assert len(cds_feature) <= 1, '#: {}, id: {}'.format(len(cds_feature), rec.id)

        # return if there is no cds
        if len(cds_feature) == 0:
            return ccds, location

        cds_feature = cds_feature[0]
        db_xref = cds_feature.qualifiers.get('db_xref', None)
        if db_xref:
            x = [x for x in db_xref if x.startswith('CCDS:')]
            if len(x) == 1:
                ccds = SubStr(x[0], 'CCDS:')

        loc = ""
        locations = cds_feature.location
        if locations:
            locations = locations.parts
            for location in locations:
                # add one because it shows python counting but we want genbank counting
                # https://biopython.org/docs/1.75/api/Bio.SeqFeature.html#Bio.SeqFeature.FeatureLocation.__str__
                location = FeatureLocation(type(location.start)(location.start + 1), location.end)
                # has to convert to a string to display fuzzy location "42..>222" if converted to int fuzzy location will
                # not display
                if location.start == location.end:
                    location = str(location.start)
                else:
                    location = str(location.start) + ".." + str(location.end)

                if loc:
                    loc = loc + "," + location
                else:
                    loc = location
        return ccds, loc

