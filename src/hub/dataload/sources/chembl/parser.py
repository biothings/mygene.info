import json


def parse_data(data):
    for item in data["targets"]:
        output = {
            "chembl_target": item["target_chembl_id"],
            "xrefs": {
                "accession": (
                    [
                        target_component.get("accession")
                        for target_component in item["target_components"]
                        if "accession" in target_component
                    ]
                ),
            },
        }
        if output["xrefs"]["accession"]:
            yield output


def load_data(target_filepaths):
    for file in target_filepaths:
        with open(file) as f:
            content = f.read()
            json_data = json.loads(content)
            parsed_data = parse_data(json_data)
            return parsed_data
