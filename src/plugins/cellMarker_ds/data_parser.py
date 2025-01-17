# this file will parse the data into json

import csv
import json
import os
import re

import numpy as np
import requests
from biothings import config
from biothings.utils.dataload import dict_convert, dict_sweep

logging = config.logger
GENE_ID = "geneid"
GENE_SYMBOL = "genesymbol"
MARKER_RESOURCE = "markerresource"
CELL_INFO_KEYS = [
    "cellontologyid",
    "cellname",
    "celltype",
    "cancertype",
    "tissuetype",
    "uberonontologyid",
    "speciestype",
    "markerresource",
    "pmid",
    "company",
]
ZIP_COLUMNS = [GENE_ID, GENE_SYMBOL]
FILES = ["all_cell_markers.txt", "Single_cell_markers.txt"]


def get_gene_symbol(gene_ids: str) -> str:
    """The function that make an API request to my mygene.info, requesting for symbol using gene ID

    Args:
        gene_id (str): the id of the gene

    Returns:
        (str) the symbol of the gene
    """
    headers = {"content-type": "application/x-www-form-urlencoded"}
    params = f"ids={gene_ids}&fields=symbol"

    try:
        res = requests.post("http://mygene.info/v3/gene", data=params, headers=headers)
        res.raise_for_status()
    except requests.RequestException as e:
        return {}

    return json.loads(res.content.decode("utf-8"))


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


def pairUp_seq_info(value_dict: dict) -> list:
    """Pair up all the elements in each value of the dictionary

    Args:
        value_dict (dict): values that need to be paired up

    Returns:
        list[dict]: A list of dictionaries where each dict contains a pairing
        of keys with corresponding elements from the value lists.
    >>> pairUp_seq_info({"a": "1, 2", "b": "3, 4"})
    [{'a': '1', 'b': '3'}, {'a': '2', 'b': '4'}]
    >>> pairUp_seq_info({"a": '1'})
    [{'a': '1'}]
    """
    keys = list(value_dict.keys())
    values = [str_to_list(value) for value in value_dict.values()]

    if not all(len(v) == len(next(iter(values))) for v in values):
        gene_ids = ", ".join(
            [
                gene_id
                for gene_id in str_to_list(value_dict["geneid"])
                if gene_id.casefold() != "na" and gene_id != ""
            ]
        )
        symbols = get_gene_symbol(gene_ids)

        return [
            {"geneid": gene_info["_id"], "genesymbol": gene_info["symbol"]}
            for gene_info in symbols
        ]

    return [dict(zip(keys, combination)) for combination in zip(*values)]


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


def load_annotations(data_folder):
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

        # ignore geneID that is missing
        if record[GENE_ID].casefold() == "na" or record[GENE_ID].casefold() == "":
            continue
        # zip these elements together to get multiple copies
        for gene_expression in pairUp_seq_info(select_items(record, ZIP_COLUMNS)):
            _id = gene_expression["geneid"]
            if _id.casefold() == "na" or _id.casefold() == "":
                continue
            results.setdefault(_id, {})
            gene_expression_dict = results[_id]
            gene_expression_dict["symbol"] = gene_expression["genesymbol"]
            if record["markerresource"].casefold() != "company":
                gene_expression_dict.setdefault("geneRelatedCells", []).append(
                    dict_sweep(
                        {
                            "CellOntologyID": record["cellontologyid"],
                            "cellName": record["cellname"],
                            "cellType": record["celltype"],
                            "cancerType": record["cancertype"],
                            "tissueType": record["tissuetype"],
                            "UberonOntologyID": record["uberonontologyid"],
                            "speciesType": record["speciestype"],
                            "markerResource": record["markerresource"],
                            "PMID": record["pmid"],
                        }
                    )
                )
            else:
                gene_expression_dict.setdefault("geneRelatedCells", []).append(
                    dict_sweep(
                        {
                            "CellOntologyID": record["cellontologyid"],
                            "cellName": record["cellname"],
                            "cellType": record["celltype"],
                            "cancerType": record["cancertype"],
                            "tissueType": record["tissuetype"],
                            "UberonOntologyID": record["uberonontologyid"],
                            "speciesType": record["speciestype"],
                            "markerResource": record["markerresource"],
                            "Company": record["company"],
                        }
                    )
                )
    # return each gene_id with yield and remove duplicate from the dictionary
    for _id, related_info in results.items():
        yield {
            "_id": _id,
            "symbol": related_info["symbol"],
            "geneRelatedCells": make_uniqueMarker(related_info["geneRelatedCells"]),
        }


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    x = load_annotations("data")
    y = [i for i in x]
    breakpoint()
