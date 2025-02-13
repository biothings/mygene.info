# this file will parse the data into json

import csv
import json
import os
import re

import requests
from biothings.utils.dataload import dict_convert, dict_sweep

GENE_ID = "geneid"
GENE_SYMBOL = "genesymbol"
MARKER_RESOURCE = "markerresource"
FILES = ["all_cell_markers.txt", "Single_cell_markers.txt"]


def str_to_list(listLikeStr: str) -> list:
    """Case str-like-list into actual list, nested list will be expand

    Args:
        listLikeStr (str): the list like str

    Return:
        the converted list

    >>> str_to_list("A")
    ['A']
    >>> str_to_list("A, B")
    ['A', 'B']
    >>> str_to_list("A B")
    ['A B']
    >>> str_to_list("A, [A, B], C")
    ['A', 'A', 'B', 'C']
    >>> str_to_list("A, B, C, D, [E, F], [G, H I]")
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H I']
    """
    parsed_str = re.sub(r"[\[\]]", "", listLikeStr)
    parsed_str_list = parsed_str.split(",")
    return [val.strip() for val in parsed_str_list]


def make_uniqueMarker(cellMarkers: list) -> list:
    """Make unique markers from a list of cell markers

    Args:
        cellMarkers (list): list of cell markers

    Returns:
        list: list of unique cell markers
    """
    cellMarkers = list({tuple(sorted(marker.items())) for marker in cellMarkers})
    return [dict(marker) for marker in cellMarkers]


def select_items(record, item_keys):
    """Select specific items from a record

    Args:
        record (dict): the record to select items from
        item_keys (list): the keys of the items to select

    Returns:
        dict: the selected items
    """
    return {key: record[key] for key in item_keys if key in record}


def load_data_files(data_folder: str, files: list) -> list:
    """
    Load data from a list of files in a specified folder.
    Args:
        data_folder (str): The path to the folder containing the data files.
        files (list): A list of filenames to be loaded from the data folder.

    Returns:
        list[dict]: A list of dictionaries containing the data from the files.

    Raises:
        FileNotFoundError: If any of the specified files do not exist in the data folder.
    """
    data = []
    for file in files:
        file_path = os.path.join(data_folder, file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing file: {file_path}")
        with open(file_path, mode="r") as f:
            reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
            data.extend(reader)
    return data


def load_cellMarkers(data_folder):
    """Converting data into expected JSON format

    Args:
        data_folder (str): the relative data path to the data source

    Return:
        the yield JSON data
    """
    # load data
    data = load_data_files(data_folder, FILES)

    results = {}
    for record in data:
        # converting all the key to standard format
        record = dict_convert(record, keyfn=lambda k: k.replace(" ", "_").lower())

        # ignore geneID that is missing or contains non-numeric value
        if record[GENE_ID].casefold() == "na" or not record[GENE_ID].isnumeric() or record[GENE_ID].casefold() == "":
            continue

        # zip these elements together to get multiple copies
        for gene_id in str_to_list(record[GENE_ID]):
            _id = gene_id
            if _id.casefold() == "na" or _id.casefold() == "":
                continue
            results.setdefault(_id, {})
            gene_id_dict = results[_id]

            # identify source key
            if record["markerresource"].casefold() != "company":
                resource_key = "pmid"
                record_resource_key = "pmid"
            else:
                resource_key = "company"
                record_resource_key = "company"

            # handle edge case
            # if tissuetype is undefined, we will make it empty
            if record["tissuetype"].casefold() == "undefined":
                record["tissuetype"] = ""

            # check if any value in the dict is na, if so, make it empty
            for key, value in record.items():
                # handle missing values
                if value.casefold() == "na":
                    record[key] = ""

                if key == "cellontologyid" or key == "uberonontologyid":
                    record[key] = record[key].replace("_", ":")
                else:
                    record[key] = record[key].lower()

            gene_id_dict.setdefault("cellmarker", []).append(
                dict_sweep(
                    {
                        "cellontology": record["cellontologyid"],
                        "cellname": record["cellname"],
                        "celltype": record["celltype"],
                        "cancertype": record["cancertype"],
                        "tissue": record["tissuetype"],
                        "uberon": record["uberonontologyid"],
                        "species": record["speciestype"],
                        "marker_resource": record["markerresource"],
                        f"{resource_key}": record[f"{record_resource_key}"],
                    }
                )
            )

    # return each gene_id with yield and remove duplicate from the dictionary
    for _id, related_info in results.items():
        yield {
            "_id": _id,
            "cellmarker": make_uniqueMarker(related_info["cellmarker"]),
        }


# if __name__ == "__main__":
#     import doctest

#     doctest.testmod()
#     x = load_cellMarkers("data")
#     y = [i for i in x]

#     breakpoint()
