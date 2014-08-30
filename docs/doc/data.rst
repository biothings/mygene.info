.. Data

Gene annotation data
*********************

.. _data_sources:

Data sources
------------

We currently obtain the gene annotation data from several public data resources and keep them up-to-date, so that you don't have to do it:

============    =======================      =================================
Source           Update frequency               Notes
============    =======================      =================================
NCBI Entrez      weekly snapshot
Ensembl          whenever a new              | Ensembl Pre! and EnsemblGenomes
                 release is available        | are not included at the moment
Uniprot          whenever a new
                 release is available
NetAffy          whenever a new
                 release is available
PharmGKB         whenever a new
                 release is available
UCSC             whenever a new               For "exons" field
                 release is available
CPDB             whenever a new               For "pathway" field
                 release is available

============    =======================      =================================

The most updated data information can be accessed `here <http://mygene.info/v2/metadata>`_.

.. _gene_object:

Gene object
------------
Gene annotation data are both stored and returned as a gene object, which is essentially a collection of fields (attributes) and their values:

.. code-block :: json

    {
        "_id": "1017"
        "taxid": 9606,
        "symbol": "CDK2",
        "entrezgene": 1017,
        "name": "cyclin-dependent kinase 2",
        "genomic_pos": {
            "start": 56360553,
            "chr": "12",
            "end": 56366568,
            "strand": 1
        }
    }

The example above omits most of available fields. For a full example, you can just check out a few gene examples: `CDK2 <http://mygene.info/v2/gene/1017>`_, `ADA <http://mygene.info/v2/gene/100>`_. Or, did you try our `interactive API page <http://mygene.info/v2/api>`_ yet?

.. _species:

Species
------------
We support **ALL** species annotated by NCBI and Ensembl. All of our services allow you to pass a "**species**" parameter to limit the query results. "species" parameter accepts taxonomy ids as the input. You can look for the taxomony ids for your favorite species from `NCBI Taxonomy <http://www.ncbi.nlm.nih.gov/taxonomy>`_.

For convenience, we allow you to pass these *common names* for commonly used species (e.g. "species=human,mouse,rat"):

.. container:: species-table

    ===========  =======================    ===========
    Common name  Genus name                 Taxonomy id
    ===========  =======================    ===========
    human        Homo sapiens               9606
    mouse        Mus musculus               10090
    rat          Rattus norvegicus          10116
    fruitfly     Drosophila melanogaster    7227
    nematode     Caenorhabditis elegans     6239
    zebrafish    Danio rerio                7955
    thale-cress  Arabidopsis thaliana       3702
    frog         Xenopus tropicalis         8364
    pig          Sus scrofa                 9823
    ===========  =======================    ===========

If needed, you can pass "species=all" to query against all available species, although, we recommend you to pass specific species you need for faster response.


.. _genome_assemblies:

Genome assemblies
----------------------------

Our `gene query service <query_service.html>`_ supports `genome interval queries <query_service.html#genome-interval-query>`_. We import genomic location data from Ensembl, so all species available there are supported. You can find the their reference genome assemblies information `here <http://www.ensembl.org/info/about/species.html>`_.


This table lists the genome assembies for commonly-used species:

.. container:: species-table

    ===========  =======================   =======================
    Common name  Genus name                Genome assembly
    ===========  =======================   =======================
    human        Homo sapiens              GRCh38 (hg38)
    mouse        Mus musculus              GRCm38 (mm10)
    rat          Rattus norvegicus         Rnor_5.0 (rn4)
    fruitfly     Drosophila melanogaster   BDGP5 (dm3)
    nematode     Caenorhabditis elegans    WBcel235 (ce10)
    zebrafish    Danio rerio               Zv9 (danRer6)
    frog         Xenopus tropicalis        JGI_4.2 (xenTro2)
    pig          Sus scrofa                Sscrofa10.2 (susScr2)
    ===========  =======================   =======================




.. raw:: html

    <div id="spacer" style="height:300px"></div>
