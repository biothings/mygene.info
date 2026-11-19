
import requests

from biothings.web.handlers import MetadataSourceHandler, QueryHandler

# Data sources and uploaders renamed in the hub. /metadata keeps listing the old names as
# deprecated aliases so clients that look sources up by name keep working for a while.
# Remove these tables and add_renamed_source_aliases() when the deprecation period ends.
RENAMED_SOURCES = {
    # old source name: new source name
    "entrez": "ncbi_gene",
    "entrez_unigene": "unigene",
    "mygene_unii": "unii",
}
RENAMED_UPLOADERS = {
    # old uploader name: new uploader name
    "entrez_gene": "ncbi_gene_info",
    "entrez_accession": "ncbi_gene_accession",
    "entrez_go": "ncbi_gene_go",
    "entrez_genomic_pos": "ncbi_gene_genomic_pos",
    "entrez_retired": "ncbi_gene_retired",
    "entrez_refseq": "ncbi_gene_refseq",
    "entrez_unigene": "unigene",
    "mygene_unii": "unii",
    "entrez_genesummary": "refseq_summary",
    "entrez_ec": "refseq_ec",
}
# the parts of a source's metadata that are keyed by uploader name
UPLOADER_KEYED_FIELDS = ("stats", "upload_date", "code")
_UPLOADER_KEYED_FIELDS_TEXT = "stats, upload_date and code"


def _add_old_uploader_names(source, keep_new):
    """
    Return a copy of a source's metadata whose uploader-keyed fields use the old uploader
    names, and a dict {old: new} of the names it changed.

    With keep_new, the old names are added next to the new ones instead of replacing them.
    The copies are shallow: the values they share with ``source`` must not be modified.
    """
    source = dict(source)
    renamed = {}
    for field in UPLOADER_KEYED_FIELDS:
        if not isinstance(source.get(field), dict):
            continue  # e.g. upload_date or code of a single-uploader source
        value = source[field] = dict(source[field])
        for old, new in RENAMED_UPLOADERS.items():
            if new in value and old not in value:
                value[old] = value[new] if keep_new else value.pop(new)
                renamed[old] = new
    return source, renamed


def _list_renames(renamed):
    return ", ".join(f"{old} to {new}" for old, new in renamed.items())


def add_renamed_source_aliases(src):
    """
    Return a copy of the metadata's ``src`` with deprecated aliases for renamed sources and
    uploaders, and a warning listing them (None if nothing was added).

    - A renamed source is also listed under its old name, as a copy of its entry that uses
      the old uploader names (e.g. src.entrez.stats.entrez_gene).
    - A source that kept its name but has renamed uploaders (refseq) also lists the old
      uploader names, next to the new ones.

    Old names already in ``src`` are left alone, so the metadata of a build made before the
    rename comes back unchanged. ``src`` itself is not modified.
    """
    src = dict(src)
    new_to_old = {new: old for old, new in RENAMED_SOURCES.items()}
    renamed_sources = {}
    renamed_uploaders = {}

    for name, source in list(src.items()):
        if not isinstance(source, dict):
            continue
        old_name = new_to_old.get(name)
        if old_name:
            if old_name in src:
                continue
            alias, renamed = _add_old_uploader_names(source, keep_new=False)
            alias["_warning"] = (
                f"Deprecated: {old_name} was renamed to {name}. Use src.{name} instead; "
                "this alias will be removed in a future release."
            )
            src[old_name] = alias
            renamed_sources[old_name] = name
        else:
            source, renamed = _add_old_uploader_names(source, keep_new=True)
            if renamed:
                source["_warning"] = (
                    f"Deprecated: renamed uploaders ({_list_renames(renamed)}) are also listed "
                    f"under their old names in {_UPLOADER_KEYED_FIELDS_TEXT}; the old names "
                    "will be removed in a future release."
                )
                src[name] = source
        # the stats key of a single-uploader source is the source name, already listed above
        renamed_uploaders.update(
            (old, new) for old, new in renamed.items() if RENAMED_SOURCES.get(old) != new
        )

    if not renamed_sources and not renamed_uploaders:
        return src, None

    warning = "Some data sources were renamed"
    if renamed_sources:
        warning += f" ({_list_renames(renamed_sources)})"
    if renamed_uploaders:
        warning += (
            f", along with uploaders listed in {_UPLOADER_KEYED_FIELDS_TEXT} "
            f"({_list_renames(renamed_uploaders)})"
        )
    warning += (
        ". src still lists the old names as aliases, but they are deprecated and will be "
        "removed in a future release. Gene fields and queries are not affected."
    )
    return dict(sorted(src.items())), warning


class MygeneQueryHandler(QueryHandler):

    async def get(self, *args, **kwargs):

        if self.args.include_tax_tree and 'all' not in self.args.species:

            res = requests.post(
                self.settings['biothings'].INCLUDE_TAX_TREE_REDIRECT_ENDPOINT,
                data={
                    "ids": ','.join([str(sid) for sid in self.args.species]),
                    "expand_species": 'True'
                },
                headers={
                    'user-agent': (
                        'Python-requests_'
                        'mygene.info/'
                        '{} (gzip)'
                    ).format(requests.__version__)
                })

            if res.status_code == requests.codes.ok:
                self.args.species = [str(x) for x in res.json()]

        await super().get(self, *args, **kwargs)


class MygeneSourceHandler(MetadataSourceHandler):
    """
    GET /metadata
    GET /v3/metadata

    {
        "biothing_type": "gene",
        "build_date": "2020-03-29T04:00:00.012426",
        "build_version": "20200329",
        "genome_assembly": {
            "human": "hg38",
            "mouse": "mm10",
            ...
        },
        "src": { ... }, // 28 items
        "stats": {
            "total": 36232158,
            "total_genes": 36232158,
            "total_entrez_genes": 27119488,
            "total_ensembl_genes": 38915576,
            "total_ensembl_genes_mapped_to_entrez": 5954466,
            "total_ensembl_only_genes": 9112670,
            "total_species": 28605
        },
        "taxonomy": {
            "human": 9606,
            "mouse": 10090,
            ...
        }
    }
    """

    def extras(self, _meta):

        _meta['taxonomy'] = {}
        _meta['genome_assembly'] = {}

        for s, d in self.biothings.config.TAXONOMY.items():
            if 'tax_id' in d:
                _meta['taxonomy'][s] = int(d['tax_id'])
            if 'assembly' in d:
                _meta['genome_assembly'][s] = d['assembly']

        if isinstance(_meta.get('src'), dict):
            _meta['src'], warning = add_renamed_source_aliases(_meta['src'])
            if warning:
                _meta['_warning'] = warning

        return _meta
