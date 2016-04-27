'''
Utils for running parallel jobs on IPython cluster.
'''
from __future__ import print_function
import time
import copy
from IPython.parallel import Client

from config import CLUSTER_CLIENT_JSON
from utils.common import timesofar, ask


def run_jobs_on_ipythoncluster(worker, task_list, shutdown_ipengines_after_done=False):

    t0 = time.time()
    rc = Client(CLUSTER_CLIENT_JSON)
    lview = rc.load_balanced_view()
    cnt_nodes = len(lview.targets or rc.ids)
    print("\t# nodes in use: {}".format(cnt_nodes))
    lview.block = False

    print("\t# of tasks: {}".format(len(task_list)))
    print("\tsubmitting...", end='')
    job = lview.map_async(worker, task_list)
    print("done.")
    try:
        job.wait_interactive()
    except KeyboardInterrupt:
        #handle "Ctrl-C"
        if ask("\nAbort all submitted jobs?") == 'Y':
            lview.abort()
            print("Aborted, all submitted jobs are cancelled.")
        else:
            print("Aborted, but your jobs are still running on the cluster.")
        return

    if len(job.result) != len(task_list):
        print("WARNING:\t# of results returned ({}) != # of tasks ({}).".format(len(job.result), len(task_list)))
    print("\ttotal time: {}".format(timesofar(t0)))

    if shutdown_ipengines_after_done:
        print("\tshuting down all ipengine nodes...", end='')
        lview.shutdown()
        print('Done.')
    return job.result


def collection_partition(src_collection_list, step=100000):
    if not isinstance(src_collection_list, (list, tuple)):
        src_collection_list = [src_collection_list]

    kwargs = {}
    kwargs['limit'] = step
    for src_collection in src_collection_list:
        _kwargs = copy.copy(kwargs)
        _kwargs['src_collection'] = src_collection.name
        _kwargs['src_db'] = src_collection.database.name
        _kwargs['server'] = src_collection.database.connection.host
        _kwargs['port'] = src_collection.database.connection.port

        cnt = src_collection.count()
        for s in range(0, cnt, step):
            __kwargs = copy.copy(_kwargs)
            __kwargs['skip'] = s
            yield __kwargs
