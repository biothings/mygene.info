import requests
import json
import logging
import time
import multiprocessing as mp

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_handler = logging.FileHandler('pharos.log')
logger_handler.setLevel(logging.DEBUG)
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)

MAX_TARGET_NUMBER = 20244
URL_TEMPLATE = "https://pharos.nih.gov/idg/api/v1/targets(ID)/synonyms(label=Entrez%20Gene)"

def query_single_pharos_target_id(pharos_id):
    try:
        response = requests.get(URL_TEMPLATE.replace('ID', str(pharos_id)))
    except ConnectionError as e:
        logging.exception(e, exc_info=True)
        response = None
    if response and response.ok:
        data = response.json()
        entrez_id = [int(_doc['term']) for _doc in data]
        if len(entrez_id) > 1:
            logger.warn('Found pharos target ID %s corresponding to more than one entrez gene ids', i)
            for _id in entrez_id:
                return {
                    'entrez_gene_id': _id,
                    'pharos_target_id': pharos_id
                }
        elif len(entrez_id) == 1:
            entrez_id = entrez_id[0]
            return {
                'entrez_gene_id': entrez_id,
                'pharos_target_id': pharos_id
            }
        else:
            logger.warn('Found pharos target ID %s having no corresponding entrez gene ids', i)
    else:
        logger.warn('No hits for pharos target ID %s', i)

def load_data():
    logger.info('Start processing pharos target IDs')
    results = []
    start_time = time.clock()
    core_count = mp.cpu_count()
    pool = mp.Pool(processes=core_count)
    logger.info('Running on machine with %s cores', core_count)
    for i in range(1, MAX_TARGET_NUMBER+1, 1000):
        tmp = pool.map(query_single_pharos_target_id, range(i, i+1000))
        logger.info('Processed %s pharos target IDs!', i + 999)
        logger.info('Total time used to process these docs is %s', time.clock() - start_time)
        results += tmp
        start_time = time.clock()
    return results