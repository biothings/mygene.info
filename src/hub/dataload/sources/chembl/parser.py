import json
import re


def parse_data(data):
    chembl_dict = {}

    # https://www.uniprot.org/help/accession_numbers
    UNIPROT_ACCESSION_PATTERN = re.compile(
        r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}"
    )

    for item in data["targets"]:
        uniprot_accessions = []
        accessions = (
            component["accession"].rstrip()
            for component in item.get("target_components")
            if component["accession"]
        )
        for accession in accessions:
            if UNIPROT_ACCESSION_PATTERN.fullmatch(accession):
                uniprot_accessions.append(accession)
        if uniprot_accessions:
            for uniprot_accession in uniprot_accessions:
                uniprot = uniprot_accession
                chembl_target = item["target_chembl_id"]
                if uniprot in chembl_dict:
                    if isinstance(chembl_dict[uniprot]["chembl_target"], list):
                        chembl_dict[uniprot]["chembl_target"].append(chembl_target)
                    else:
                        chembl_dict[uniprot]["chembl_target"] = [
                            chembl_dict[uniprot]["chembl_target"],
                            chembl_target,
                        ]
                else:
                    chembl_dict[uniprot] = {
                        "chembl_target": chembl_target,
                        "uniprot": uniprot,
                    }
    for uniprot, chembl in chembl_dict.items():
        yield {"chembl": chembl}


def load_data(target_filepaths):
    for file in target_filepaths:
        with open(file) as f:
            content = f.read()
            json_data = json.loads(content)
            for data in parse_data(json_data):
                yield data
