# HGNC Data Plugin
Data Plugin for **[BioThings API](https://biothings.io/)**.
Data is uploaded from the **HUGO Gene Nomenclature Committee ([HGNC](https://www.genenames.org/download/archive/))** complete set, released under [CC0](https://www.genenames.org/about/license/).

## Notes

- Adds `prev_symbol`: the former official symbols of renamed human genes (e.g. `PARK2` for `PRKN`).
  NCBI gene_info merges these into Synonyms (our `alias` field), so they could not be told apart
  from casual synonyms or ranked above them. See [mygene.info#172](https://github.com/biothings/mygene.info/issues/172).
- Keyed by the `entrez_id` column, so no ID translation is needed. Rows without an Entrez gene id are skipped.
- Values equal to the gene's current symbol are dropped. Like `alias`, a single value is stored as a string and several as a sorted list.
- The default query scores `prev_symbol` just below `symbol` for single-term queries (see `symbol_queries()` in `src/web/pipeline/legacy.py`).

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
