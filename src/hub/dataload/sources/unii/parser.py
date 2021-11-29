import requests
from biothings_client import get_client
from collections import defaultdict


try:
    from biothings import config
    logger = config.logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


GENE_CLIENT = get_client('gene')


def query_uniprot(uniprot: list):
    """Use biothings_client.py to query uniprot codes and get back '_id' in mygene.info

    :param: uniprot: list of uniprot codes
    """
    res = GENE_CLIENT.querymany(uniprot, scopes='uniprot', fields='_id', returnall=True)
    new_res = defaultdict(list)
    for item in res['out']:
        if not "notfound" in item:
            new_res[item['query']].append(item['_id'])
    return [new_res, res]


def get_uniprot():
    """Requests the fda api to return uniprot: unii dictionary

    """

    # make a request to the fda api
    url = "https://api.fda.gov/other/substance.json?search=codes.code_system:%22UNIPROT%22&"
    request = requests.get(url).json()
    doc = {}

    # error checking 26000
    if request["meta"]["results"]["total"] > 26000:
        logger.error("Exceeds limit to paginate see this page for more details: https://open.fda.gov/apis/paging/")
        raise RuntimeError('Limit Exceeded')
    else:
        count = (request["meta"]["results"]["total"]-1)//1000

    # paginate through the api and collect protein: unii
    for page in range(count+1):
        url = "https://api.fda.gov/other/substance.json?search=codes.code_system:%22UNIPROT%22&limit=1000&skip=" + str(page*1000)
        request = requests.get(url).json()
        for result in request["results"]:
            for code in result["codes"]:
                if code["code_system"] == "UNIPROT":
                    if code["code"] in doc.keys():
                        doc[code["code"]].append(result["unii"])
                    else:
                        doc[code["code"]] = [result["unii"]]
                else:
                    continue
    return doc


def load_uniprot():
    docs = get_uniprot()
    ids = query_uniprot(list(docs.keys()))
    logger.info("This is the number of missing uniprot to gene_id: %d", len(ids[1]['missing']))
    logger.debug("This is the list of missing uniprot to gene_id: %s", ids[1]['missing'])
    for prot, unii in docs.items():
        gene_ids = ids[0][prot]
        for gene_id in gene_ids:
            rec = {
                "_id": gene_id,
                "unii": unii
            }
            yield rec


