'''
This module monitors src_dump collection in MongoDB, dispatch dataloading
jobs when new data files are available.

    python -u -m dataload/dispatch -d

    * with "-d" parameter, it will continue monitoring,
      without "-d", it will quit after all running jobs are done.

'''
from subprocess import Popen, STDOUT, check_output
import time
from datetime import datetime
import sys
import os.path
from biothings.utils.mongo import get_src_dump
from biothings.utils.common import safewfile, timesofar

src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
sys.path.append(src_path)

src_dump = get_src_dump()


def check_mongo():
    '''Check for "pending_to_upload" flag in src_dump collection.
       And return a list of sources should be uploaded.
    '''
    # filter some more: _id is supposed to be a user-defined string, not an ObjectId()
    return [src['_id'] for src in src_dump.find({'pending_to_upload': True}) if type(src['_id']) == str]


def dispatch(src):
    src_doc = src_dump.find_one({'_id': src})
    datadump_logfile = src_doc.get('logfile', '')
    if datadump_logfile:
        upload_logfile = os.path.join(os.path.split(datadump_logfile)[0], '{}_upload.log'.format(src))
    else:
        from config import DATA_ARCHIVE_ROOT
        upload_logfile = os.path.join(DATA_ARCHIVE_ROOT, '{}_upload.log'.format(src))

    log_f, logfile = safewfile(upload_logfile, prompt=False, default='O')
    p = Popen(['python', '-u', '-m', 'dataload.start', src],
              stdout=log_f, stderr=STDOUT, cwd=src_path)
    p.logfile = logfile
    p.log_f = log_f
    return p


def mark_upload_started(src):
    src_dump.update({'_id': src}, {"$unset": {'pending_to_upload': "",
                                              'upload': ""}})
    src_dump.update({'_id': src}, {"$set": {"upload.status": "uploading",
                                            "upload.started_at": datetime.now()}})


def mark_upload_done(src, d):
    src_dump.update({'_id': src}, {"$set": d})


def get_process_info(running_processes):
    name_d = dict([(str(p.pid), name) for name, p in running_processes.items()])
    pid_li = name_d.keys()
    if pid_li:
        output = check_output(['ps', '-p', ' '.join(pid_li)])
        output = output.decode("utf8").split('\n')
        output[0] = '    {:<10}'.format('JOB') + output[0]  # header
        for i in range(1, len(output)):
            line = output[i].strip()
            if line:
                pid = line.split()[1]
                output[i] = '    {:<10}'.format(name_d.get(pid, '')) + output[i]
    return '\n'.join(output)


def main(daemon=False):
    running_processes = {}
    while 1:
        src_to_update_li = check_mongo()
        if src_to_update_li:
            print('\nDispatcher:  found pending jobs ', src_to_update_li)
            for src_to_update in src_to_update_li:
                if src_to_update not in running_processes:
                    mark_upload_started(src_to_update)
                    p = dispatch(src_to_update)
                    src_dump.update({'_id': src_to_update}, {"$set": {"upload.pid": p.pid}})
                    p.t0 = time.time()
                    running_processes[src_to_update] = p

        jobs_finished = []
        if running_processes:
            print('Dispatcher:  {} active job(s)'.format(len(running_processes)))
            print(get_process_info(running_processes))

        for src in running_processes:
            p = running_processes[src]
            returncode = p.poll()
            if returncode is not None:
                t1 = round(time.time() - p.t0, 0)
                d = {'upload.returncode': returncode,
                     'upload.timestamp': datetime.now(),
                     'upload.time_in_s': t1,
                     'upload.time': timesofar(p.t0),
                     'upload.logfile': p.logfile,
                     }
                if returncode == 0:
                    print('Dispatcher:  {} finished successfully with code {} (time: {}s)'.format(src, returncode, t1))
                    d['upload.status'] = "success"
                else:
                    print('Dispatcher:  {} failed with code {} (time: {}s)'.format(src, returncode, t1))
                    d['upload.status'] = "failed"

                mark_upload_done(src, d)
                jobs_finished.append(src)
                p.log_f.close()
            else:
                p.log_f.flush()
        for src in jobs_finished:
            del running_processes[src]

        if running_processes:
            time.sleep(10)
        else:
            if daemon:
                #continue monitor src_dump collection
                print("{}".format('\b' * 50), end='')
                for i in range(100):
                    print('\b' * 2 + [chr(8212), '\\', '|', '/'][i % 4], end='')
                    time.sleep(0.1)
            else:
                break


if __name__ == '__main__':
    run_as_daemon = '-d' in sys.argv
    main(run_as_daemon)




