# HGNC Data Plugin
Data Plugin for **[BioThings API](https://biothings.io/)**.
Data is uploaded from the **HUGO Gene Nomenclature Committee ([HGNC](https://www.genenames.org/download/archive/))** complete set, released under [CC0](https://www.genenames.org/about/license/).

## Notes

- Adds `prev_symbol`: the former official symbols of renamed human genes (e.g. `PARK2` for `PRKN`).
  NCBI gene_info merges these into Synonyms (our `alias` field), so they could not be told apart
  from casual synonyms or ranked above them. See [mygene.info#172](https://github.com/biothings/mygene.info/issues/172).
- Keyed by the `entrez_id` column, so no ID translation is needed. Rows without an Entrez gene id are skipped.
- Values equal to the gene's current symbol are dropped. Like `alias`, a single value is stored as a string and several as a list.
- HGNC occasionally lists the same Entrez gene id on two approved records for a few weeks, so the uploader uses `on_duplicates: merge` to keep both records' former symbols instead of failing the upload.
- For single-term queries, the default query ranks a human `prev_symbol` hit below exact `symbol` hits in the common species weighted in `src/web/pipeline/build.py`, and above other species' exact `symbol` hits (see `symbol_queries()` in `src/web/pipeline/legacy.py`).

## <u> Document Structure </u>

```
[
    {
        "_id": "5071",
        "prev_symbol": "PARK2"
    },
    {
        "_id": "29104",
        "prev_symbol": ["C21orf127", "N6AMT1"]
    },
    .
    .
    .
]
```
