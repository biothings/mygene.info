import csv

from biothings.utils.dataload import open_anyfile, unlist


def load_data(input_file):
    with open_anyfile(input_file) as in_f:
        reader = csv.DictReader(in_f)
        result = {}
        for row in reader:
            uniprot = row.get("uniprot_id")
            if not uniprot:
                continue
            tdl = row.get("tdl")
            ncbi_id = row.get("ncbi_id")
            entry = result.setdefault(uniprot, {"tdl": set(), "ncbi_id": set()})
            if tdl:
                entry["tdl"].add(tdl)
            if ncbi_id:
                entry["ncbi_id"].add(ncbi_id)
        for uniprot, entry in result.items():
            pharos = {
                "tdl": sorted(entry["tdl"]),
                "uniprot": uniprot,
            }
            if entry["ncbi_id"]:
                # yield one doc per ncbi_id so _id is always a scalar
                for ncbi_id in sorted(entry["ncbi_id"]):
                    yield unlist({"_id": str(ncbi_id), "pharos": pharos})
            else:
                # no ncbi_id: keylookup resolves the gene id from pharos.uniprot
                yield unlist({"pharos": pharos})
