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

The most updated data information can be accessed `here <http://mygene.info/v3/metadata>`__.

.. _gene_object:

Gene object
------------
Gene annotation data are both stored and returned as a gene object, which is essentially a collection of fields (attributes) and their values:

.. code-block :: json

    {
        "_id": "1017"
        "_score": 20.4676,
        "taxid": 9606,
        "symbol": "CDK2",
        "entrezgene": 1017,
        "name": "cyclin-dependent kinase 2",
        "genomic_pos": {
            "start": 55966769,
            "chr": "12",
            "end": 55972784,
            "strand": 1
        }
    }

The example above omits most of available fields. For a full example, you can just check out a few gene examples: `CDK2 <http://mygene.info/v3/gene/1017>`_, `ADA <http://mygene.info/v3/gene/100>`_. Or, did you try our `interactive API page <http://mygene.info/v3/api>`_ yet?

_id field
---------

Each individual gene object contains an "**_id**" field as the primary key. The value of the "**_id**" field is the NCBI gene ID (the same as "entrezgene" field, but as a string) if available for a gene object, otherwise, Ensembl gene ID is used (e.g. those Ensembl-only genes). Here is `an example <http://mygene.info/v3/gene/ENSG00000274236>`_. We recommend to use "**entrezgene**" field for the NCBI gene ID, and "**ensembl.gene**" field for Ensembl gene ID, instead of using "**_id**" field.

.. note:: Regardless how the value of the "**_id**" field looks like, either NCBI gene ID or Ensembl gene ID always works for our gene annotation service `/v3/gene/\<geneid\> <http://docs.mygene.info/en/latest/doc/annotation_service.html#get-request>`_.


_score field
------------
You will often see a "**_score**" field in the returned gene object, which is the internal score representing how well the query matches the returned gene object. It probably does not mean much in `gene annotation service <http://docs.mygene.info/en/latest/doc/annotation_service.html>`_ when only one gene object is returned. In `gene query 
service <http://docs.mygene.info/en/latest/doc/query_service.html>`__, by default, the returned gene hits are sorted by the scores in descending order.


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

Our `gene query service <query_service.html>`__ supports `genome interval queries <query_service.html#genome-interval-query>`_. We import genomic location data from Ensembl, so all species available there are supported. You can find the their reference genome assemblies information `here <http://www.ensembl.org/info/about/species.html>`__.


This table lists the genome assembies for commonly-used species:

.. container:: species-table

    ===========  =======================   =======================
    Common name  Genus name                Genome assembly
    ===========  =======================   =======================
    human        Homo sapiens              GRCh38 (hg38), also support hg19
    mouse        Mus musculus              GRCm38 (mm10), also support mm9
    rat          Rattus norvegicus         Rnor_6.0 (rn6)
    fruitfly     Drosophila melanogaster   BDGP6 (dm6)
    nematode     Caenorhabditis elegans    WBcel235 (ce11)
    zebrafish    Danio rerio               GRCz10 (danRer10)
    frog         Xenopus tropicalis        JGI_7.0 (xenTro7)
    pig          Sus scrofa                Sscrofa10.2 (susScr3)
    ===========  =======================   =======================


Available fields
----------------

The table below lists of all of the possible fields that could be in a gene object.

.. raw:: html

    <table class='indexed-field-table stripe'>
        <thead>
            <tr>
                <th>Field</th>
                <th>Indexed</th>
                <th>Type</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>

    <div id="spacer" style="height:300px"></div>
