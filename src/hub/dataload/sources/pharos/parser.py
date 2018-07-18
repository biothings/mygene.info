import requests
import json
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_handler = logging.FileHandler('pharos.log', mode='w')
logger_handler.setLevel(logging.DEBUG)
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)

MAX_TARGET_NUMBER = 20244
URL_TEMPLATE = "https://pharos.nih.gov/idg/api/v1/targets(ID)/synonyms(label=Entrez%20Gene)"

def load_data():
    logger.info('Start processing pharos target IDs')
    start_time = time.clock()
    for i in range(1, MAX_TARGET_NUMBER+1):
        if i % 1000 == 0:
            logger.info('Processed %s pharos target IDs!', i)
            logger.info('Total time used to process these docs is %s', time.clock() - start_time)
            start_time = time.clock()
        response = requests.get(URL_TEMPLATE.replace('ID', str(i)))
        if response.ok:
            data = response.json()
            entrez_id = [int(_doc['term']) for _doc in data]
            if len(entrez_id) > 1:
                logger.warn('Found pharos target ID %s corresponding to more than one entrez gene ids', i)
                for _id in entrez_id:
                    yield {
                        '_id': _id,
                        'pharos': {'target_id': i}
                    }
            elif len(entrez_id) == 1:
                entrez_id = entrez_id[0]
                yield {
                    '_id': entrez_id,
                    'pharos': {'target_id': i}
                }
            else:
                logger.warn('Found pharos target ID %s having no corresponding entrez gene ids', i)

        else:
            logger.warn('No hits for pharos target ID %s', i)

