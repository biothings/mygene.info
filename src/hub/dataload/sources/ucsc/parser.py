import os.path
import time
from biothings.utils.common import timesofar
from biothings.utils.dataload import tab2dict, tabfile_feeder, list2dict


def load_exons_for_species(data_folder, species, exons_key='exons'):
    refflat_file = os.path.join(data_folder, species, 'database/refFlat.txt.gz')
    t0 = time.time()
    ref2exons = {}
    for ld in tabfile_feeder(refflat_file, header=0):
        refseq = ld[1]
        chr = ld[2]
        if chr.startswith('chr'):
            chr = chr[3:]
        exons = list(zip([int(x) for x in ld[9].split(',') if x],
                     [int(x) for x in ld[10].split(',') if x]))
        assert len(exons) == int(ld[8]), (len(exons), int(ld[8]))
        ref2exons.setdefault(refseq,[]).append({
            'transcript' : refseq,
            'chr': chr,
            'strand': -1 if ld[3] == '-' else 1,
            'txstart': int(ld[4]),
            'txend': int(ld[5]),
            'cdsstart': int(ld[6]),
            'cdsend': int(ld[7]),
            'position': exons
        })

    gene2exons = {}
    reflink_file = os.path.join(data_folder, '../hgFixed/database/refLink.txt.gz')
    refseq2gene = tab2dict(reflink_file, (2, 6), 0, alwayslist=False)
    for refseq in sorted(ref2exons.keys()):
        geneid = refseq2gene.get(refseq, None)
        if geneid and geneid != '0':
            if geneid not in gene2exons:
                gene2exons[geneid] = {exons_key: ref2exons[refseq]}
            else:
                gene2exons[geneid][exons_key].extend(ref2exons[refseq])

    return gene2exons


def load_exons_for_human(data_folder):
    '''We currently load exons on both hg19 and hg38 for human genes,
       so it will be loaded separately from other species.
           exons  -->   hg38
           exons_hg19  -->  hg19
    '''
    gene2exons_hg19 = load_exons_for_species(data_folder, 'Homo_sapiens', exons_key='exons_hg19')
    gene2exons = load_exons_for_species(data_folder, '../hg38')
    for gid in gene2exons_hg19:
        if gid in gene2exons:
            gene2exons[gid].update(gene2exons_hg19[gid])
        else:
            gene2exons[gid] = gene2exons_hg19[gid]
    return gene2exons


def load_exons_for_mouse(data_folder):
    '''We currently load exons on both mm9 and mm10 for mouse genes,
       so it will be loaded separately from other species.
           exons  -->   mm10
           exons_mm9  -->  mm9
    '''
    gene2exons = load_exons_for_species(data_folder, 'Mus_musculus')
    gene2exons_mm9 = load_exons_for_species(data_folder, '../mm9', exons_key='exons_mm9')
    for gid in gene2exons_mm9:
        if gid in gene2exons:
            gene2exons[gid].update(gene2exons_mm9[gid])
        else:
            gene2exons[gid] = gene2exons_mm9[gid]
    return gene2exons


def load_ucsc_exons(data_folder):
    species_data_folder = os.path.join(data_folder, 'goldenPath/currentGenomes')
    species_li = os.listdir(species_data_folder)
    print("Found {} species folders.".format(len(species_li)))
    t0 = time.time()
    gene2exons = {}
    for species in species_li:
        print(species, end='...')
        if species == 'Homo_sapiens':
            gene2exons.update(load_exons_for_human(species_data_folder))
        elif species == 'Mus_musculus':
            gene2exons.update(load_exons_for_mouse(species_data_folder))
        else:
            gene2exons.update(load_exons_for_species(species_data_folder,species))

    return gene2exons

