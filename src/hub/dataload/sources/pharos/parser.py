import csv

from biothings.utils.dataload import open_anyfile


def load_data(input_file):
    with open_anyfile(input_file) as in_f:
        reader = csv.DictReader(in_f)
        for row in reader:
            tdl = row.get("tdl")
            uniprot = row.get("uniprot_id")
            ncbi_id = row.get("ncbi_id")
            pharos = {}
            if tdl:
                pharos["tdl"] = tdl
            if uniprot:
                pharos["uniprot"] = uniprot
            json_doc = {"pharos": pharos}
            # ncbi_id isn't always present; when missing, the keylookup
            # resolves the gene id from pharos.uniprot instead
            if ncbi_id:
                json_doc["_id"] = str(ncbi_id)
            yield json_doc
