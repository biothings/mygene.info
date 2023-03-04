import os.path
from biothings.utils.common import dump, loadobj
from biothings.utils.dataload import dupline_seperator, tabfile_feeder, list2dict, value_convert

# REF: ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/README
VALID_COLUMN_NO = 22


def get_uniprot_section(uniprotkb_id):
    """
    Return either "Swiss-Prot" or "TrEMBL", two sections of UniProtKB, based on input uniprotkb_id, or entry name.

    The rule is (http://www.uniprot.org/manual/entry_name):
    - Swiss-Prot entries have a maximum of 5 characters before the "_"
    - TrEMBL entries have 6 or 10 characters before the "_" (the accession)

    Some examples:
    - TrEMBL: O61847_CAEEL, F0YED1_AURAN, A0A024RB10_HUMAN
    - Swiss-Prot: CDK2_HUMAN, CDK2_MOUSE
    """
    v = uniprotkb_id.split('_')
    if len(v) != 2:
        raise ValueError('Invalid UniprotKB ID')
    # return 'TrEMBL' if len(v[0])==6 else "Swiss-Prot"
    return 'Swiss-Prot' if len(v[0]) <= 5 else "TrEMBL"


def _dict_convert(uniprot_li):
    """
    convert [(u'E7ESI2', 'TrEMBL'), (u'P24941', 'Swiss-Prot'),
             (u'G3V5T9', 'TrEMBL'), (u'G3V317', 'TrEMBL')] into
    {'Swiss-Prot': u'P24941',
     'TrEMBL': [u'E7ESI2', u'G3V5T9', u'G3V317']}
    """
    _dict = list2dict(uniprot_li, 1)
    for k, v in _dict.items():
        if isinstance(v, list):
            _dict[k] = sorted(v)
    return {'uniprot': _dict}


def load_all(data_folder):
    """
    Load "uniprot" using yield, while building "PDB" and "PIR" data dict while reading data file.
    These dicts are then dumped (pickled) and stored later
    """

    def cvt_fn(pdb_id):
        return pdb_id.split(':')[0]

    def merge(xli, transcode=False):
        xli2 = []
        uniprot_acc, section, entrez_id, ensembl_id = xli
        if entrez_id:
            xli2.append((uniprot_acc, section, entrez_id))
        elif ensembl_id:
            if not transcode:
                raise KeyError(ensembl_id)
            try:
                entrez_id = ensembl2geneid[ensembl_id]
                # if ensembl_id can be mapped to entrez_id
                for _eid in entrez_id:
                    xli2.append((uniprot_acc, section, _eid))
            except KeyError:
                xli2.append((uniprot_acc, section, ensembl_id))
        return xli2

    def transform(xli2):
        gene2uniprot = list2dict(list(set(xli2)), 2, alwayslist=True)
        gene2uniprot = value_convert(gene2uniprot, _dict_convert, traverse_list=False)

        docs = []
        for gid, uniprot in gene2uniprot.items():
            doc = {"_id": gid}
            doc.update(uniprot)
            docs.append(doc)
        return docs

    def merge_x(xli, gene2x, transcode=False, cvt_fn=None, k=None):  # TODO why k is not used?
        xli2 = []
        entrez_id, ensembl_id, x_value = xli

        if not x_value:
            return

        if cvt_fn:
            x_value = cvt_fn(x_value)

        if entrez_id:
            xli2.append((entrez_id, x_value))
        elif ensembl_id:
            if not transcode:
                raise KeyError(ensembl_id)
            try:
                entrez_id = x_ensembl2geneid[ensembl_id]
                # if ensembl_id can be mapped to entrez_id
                for _eid in entrez_id:
                    xli2.append((_eid, x_value))
            except KeyError:
                xli2.append((ensembl_id, x_value))
        for x in xli2:
            gene2x.setdefault(x[0], []).append(x[1])

    uniprot_datafile = os.path.join(data_folder, 'idmapping_selected.tab.gz')

    # cache for uniprot
    ensembl2geneid = {}
    # cache for PDB and PIR
    x_ensembl2geneid = {}

    remains = []
    pdb_remains = []
    pir_remains = []

    # once filled, will be dumped for later storage
    gene2pdb = {}
    gene2pir = {}

    # store all PDB & PIR data while looping, the whole will be stored later
    for ld in tabfile_feeder(uniprot_datafile, header=1, assert_column_no=VALID_COLUMN_NO):
        # Uniprot data will be stored as we read line by line
        xlis = []
        pdbxlis = []
        pirxlis = []

        # raw lines for each sources
        uniprotld = [ld[0], ld[1], ld[2], ld[18]]
        pdbld = [ld[2], ld[19], ld[5]]
        pirld = [ld[2], ld[19], ld[11]]

        # UniProt
        # GeneID and EnsemblID columns may have duplicates
        for value in dupline_seperator(dupline=uniprotld, dup_idx=[2, 3], dup_sep='; '):
            value = list(value)
            value[1] = get_uniprot_section(value[1])
            value = tuple(value)
            xlis.append(value)
        # PDB
        for value in dupline_seperator(dupline=pdbld, dup_sep='; '):
            pdbxlis.append(value)

        # PIR
        for value in dupline_seperator(dupline=pirld, dup_sep='; '):
            pirxlis.append(value)

        for xli in xlis:
            # feed mapping
            if xli[2] != '' and xli[3] != '':
                ensembl2geneid.setdefault(xli[3], []).append(xli[2])
            try:
                # postpone ensemblid->entrezid resolution while parsing uniprot as the
                # full transcodification dict is only correct at the end.
                # ex:
                #     1. UniprotID-A    EntrezID-A  EnsemblID
                #     2. UniprotID-B                EnsemblID
                #     3. UniprotID-C    EntrezID-B  EnsemblID
                #
                #     UniprotID-B should be associated to both EntrezID-A and EntrezID-B,
                #     but we need to read up to line 3 to do so
                xli2 = merge(xli, transcode=False)
                if not xli2:
                    continue
                docs = transform(xli2)
                for doc in docs:
                    yield doc
            except KeyError:
                remains.append(xli)

        for xli in pdbxlis:
            if xli[0] != '' and xli[1] != '':
                x_ensembl2geneid.setdefault(xli[1], []).append(xli[0])
            try:
                merge_x(xli, gene2pdb, transcode=False, cvt_fn=cvt_fn, k="pdb")
            except KeyError:
                pdb_remains.append(xli)

        for xli in pirxlis:
            if xli[0] != '' and xli[1] != '':
                x_ensembl2geneid.setdefault(xli[1], []).append(xli[0])
            try:
                merge_x(xli, gene2pir, transcode=False)
            except KeyError:
                pir_remains.append(xli)

    # now transcode with what we have
    for remain in remains:
        try:
            xli2 = merge(remain, transcode=True)
            if not xli2:
                continue
            docs = transform(xli2)
            for doc in docs:
                yield doc
        except KeyError:
            pass

    for remain in pdb_remains:
        try:
            merge_x(remain, gene2pdb, transcode=True, cvt_fn=cvt_fn)
        except KeyError:
            pass

    for remain in pir_remains:
        try:
            merge_x(remain, gene2pir, transcode=True)
        except KeyError:
            pass

    # PDB
    def normalize(value, keyname):
        uniq = sorted(set(value))
        if len(uniq) > 1:
            return {keyname: uniq}
        else:
            return {keyname: uniq[0]}

    def normalize_pdb(value):
        return normalize(value, "pdb")

    def normalize_pir(value):
        return normalize(value, "pir")

    # PDB
    gene2pdb = value_convert(gene2pdb, normalize_pdb, traverse_list=False)
    pdb_dumpfile = os.path.join(data_folder, 'gene2pdb.pyobj')
    dump(gene2pdb, pdb_dumpfile)

    # PIR
    gene2pir = value_convert(gene2pir, normalize_pir, traverse_list=False)
    pir_dumpfile = os.path.join(data_folder, 'gene2pir.pyobj')
    dump(gene2pir, pir_dumpfile)


def load_pdb(data_folder):
    pdb_dumpfile = os.path.join(data_folder, 'gene2pdb.pyobj')
    data = loadobj(pdb_dumpfile)
    return data


def load_pir(data_folder):
    pir_dumpfile = os.path.join(data_folder, 'gene2pir.pyobj')
    data = loadobj(pir_dumpfile)
    return data
