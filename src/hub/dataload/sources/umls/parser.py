import glob
import os
import re
import urllib
import zipfile
from typing import Union

import bs4
import requests
from biothings.utils.common import open_anyfile

from .umls_secret import UMLS_API_KEY

try:
    from biothings import config

    logger = config.logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# Determine UMLS CUI to Entrez Gene id mappings for genes
# 1. Parse UMLS to determine HGNC ids for each CUI
# 2. Use HGNC to convert HGNC ids to Entrez Gene ids
from collections import defaultdict

from biothings_client import get_client

GENE_CLIENT = get_client("gene")


class ParserException(Exception):
    pass


def query_hgnc(hgnc_ids: list) -> dict:
    """Use biothings_client.py to query hgnc ids and get back '_id' in mygene.info

    :param: hgnc_ids: list of HGNC ids
    """
    res = GENE_CLIENT.querymany(hgnc_ids, scopes="HGNC", fields="_id")
    new_res = defaultdict(list)
    for item in res:
        if not "notfound" in item:
            new_res[item["query"]].append(item["_id"])
    return new_res


def query_uniprot(uniprot_ids: list) -> dict:
    """Use biothings_client.py to query uniprot ids and get back '_id' in mygene.info

    :param: uniprot_ids: list of UniProt IDs
    """
    res = GENE_CLIENT.querymany(uniprot_ids, scopes="uniprot.Swiss-Prot", fields="_id")
    new_res = defaultdict(list)
    for item in res:
        if not item.get("notfound"):
            new_res[item["query"]].append(item["_id"])
    return new_res


def parse_mrcon(archive_path, data_path: Union[str, bytes]):
    """Parse the UMLS to determine the HGNC identifier of each gene CUI.

    The relevant files are in the archive <version>-1-meta.nlm (a zip file)
    within <version>/META/MRCONSO.RRF.*.gz

    Concatenate the unzipped versions of the MRCONSO files together to get the
    final MRCONSO.RRF file, which is a | delimited text file without a header.
    """

    res = defaultdict(set)
    hgnc_ids = set()
    with open_anyfile((archive_path, data_path), "r") as fin:
        for line in fin:
            if "HGNC:" in line:
                vals = line.rstrip("\n").split("|")

                cui = vals[0]
                for val in vals[1:]:
                    if val.startswith("HGNC:"):
                        res[val.split(":")[-1]].add(cui)
                        hgnc_ids.add(val.split(":")[-1])
    return res, hgnc_ids


def parse_mrsat(archive_path, data_path: Union[str, bytes]):
    """Parse the UMLS to determine the UniProt identifier of each protein CUI.

    The relevant file is MRSAT.RRF, which is downloaded from https://download.nlm.nih.gov/umls/kss/2019AB/umls-2019AB-metathesaurus.zip
    """

    res = defaultdict(set)
    uniprot_ids = set()
    with open_anyfile((archive_path, data_path), "r") as fin:
        for line in fin:
            if "SWISS_PROT" in line:
                vals = line.rstrip("\n").split("|")
                cui = vals[0]
                res[vals[-4]].add(cui)
                uniprot_ids.add(vals[-4])
    return res, uniprot_ids


def unlist(l):
    l = list(l)
    if len(l) == 1:
        return l[0]
    return l


def get_download_url():
    res = requests.get(
        "https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html"
    )
    # Raise error if status is not 200
    res.raise_for_status()
    html = bs4.BeautifulSoup(res.text, "lxml")
    # Get the table of metathesaurus release files
    table = html.find(
        "table", attrs={"class": "usa-table border-base-lighter margin-bottom-4"}
    )
    rows = table.find_all("tr")
    # The header of the first column should be 'Release'
    assert (
        rows[0].find_all("th")[0].text.strip() == "Release"
    ), "Could not parse url from html table."
    try:
        # Get the url from the link
        url = rows[2].find_all("td")[0].a["href"]
        logger.info(f"Found UMLS download url: {url}")
        # Create the url using the api aky
        url = f"https://uts-ws.nlm.nih.gov/download?url={url}&apiKey={UMLS_API_KEY}"
        return url
    except Exception as e:
        raise ParserException(f"Can't find or parse url from table field {url}: {e}")


def load_data(data_folder):
    try:
        metathesaurus_file = glob.glob(
            os.path.join(data_folder, "*metathesaurus-release.zip")
        )[0]
    except IndexError:
        url = get_download_url()
        # Use re.sub to replace all characters after "apiKey=" with asterisks
        pii_url = re.sub(
            r"(apiKey=).*",
            r"\1" + "*" * len(re.search(r"(apiKey=)(.*)", url).group(2)),
            url,
        )
        logger.info(
            """Could not find metathesaurus archive in {}.
                     Downloading UMLS Metathesaurus file automatically:
                     {}
                     """.format(
                data_folder, pii_url
            )
        )
        # Download UMLS file to data folder
        urllib.request.urlretrieve(
            url, os.path.join(data_folder, "metathesaurus-release.zip")
        )
        # Get the downloaded file path
        metathesaurus_file = glob.glob(
            os.path.join(data_folder, "*metathesaurus-release.zip")
        )[0]
    file_list = zipfile.ZipFile(metathesaurus_file, mode="r").namelist()
    logger.info(
        "Found the following files in the metathesaurus file: {}".format(file_list)
    )
    try:
        mrsty_path = [f for f in file_list if f.endswith("MRSTY.RRF")][0]
    except IndexError:
        raise FileNotFoundError("Could not find MRSTY.RRF in archive.")
    try:
        mrconso_path = [f for f in file_list if f.endswith("MRCONSO.RRF")][0]
    except IndexError:
        raise FileNotFoundError("Could not find MRCONSO.RRF in archive.")

    hgnc_map, hgnc_ids = parse_mrcon(metathesaurus_file, mrconso_path)
    uniprot_map, uniprot_ids = parse_mrsat(metathesaurus_file, mrsty_path)
    res = {}
    hgnc2mygeneids = query_hgnc(hgnc_ids)
    uniprot2mygeneids = query_uniprot(uniprot_ids)
    for hgnc, _ids in hgnc2mygeneids.items():
        for _id in _ids:
            res[_id] = {"cui": unlist(hgnc_map[hgnc])}
    for uniprot, _ids in uniprot2mygeneids.items():
        for _id in _ids:
            if _id not in res:
                res[_id] = {}
            res[_id]["protein_cui"] = unlist(uniprot_map[uniprot])
    for _id, item in res.items():
        yield {"_id": _id, "umls": item}
