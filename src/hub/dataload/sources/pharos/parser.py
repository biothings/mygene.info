import csv

from biothings.utils.dataload import open_anyfile, unlist


def load_data(input_file):
    with open_anyfile(input_file) as in_f:
        reader = csv.DictReader(in_f)
        result = {}
        for row in reader:
            _id = row.get("ncbi_id")
            tdl = row.get("tdl")
            uniprot = row.get("uniprot_id")
            entry = result.setdefault(_id, {"tdl": set(), "uniprot": set()})
            if tdl:
                entry["tdl"].add(tdl)
            if uniprot:
                entry["uniprot"].add(uniprot)
        for _id, entry in result.items():
            json_doc = {
                "_id": str(_id),
                "pharos": {
                    "tdl": sorted(entry["tdl"]),
                    "uniprot": sorted(entry["uniprot"]),
                },
            }
            yield unlist(json_doc)
