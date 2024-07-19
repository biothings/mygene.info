from collections import defaultdict

from biothings.utils.dataload import open_anyfile, unlist


def parse_tdl(input_file):
    with open_anyfile(input_file) as f:
        result = {}
        for line in f:
            (
                _,
                _,
                _id,
                tdl,
            ) = line.strip().split(",")
            if _id and _id != "NCBI_id" and _id != "0":
                result[str(_id)] = tdl
        return result


def load_data(input_file, tdl_file):
    entrez_tdls = parse_tdl(tdl_file)

    with open_anyfile(input_file) as in_f:
        result = defaultdict(list)
        for line in in_f:
            pharos_id, _id = line.strip().split(",")
            if _id != "entrez_gene_id" and _id != "0":
                result[str(_id)].append(int(pharos_id))
        for k, v in result.items():
            if tdl := entrez_tdls.get(k):
                json_doc = {"_id": str(k), "pharos": {"target_id": v}, "tdl": tdl}
            yield unlist(json_doc)
