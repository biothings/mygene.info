import sys
import os.path
src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
sys.path.append(src_path)
import dataload

def main(source):
    '''
    Example:
        python -m dataload/start ensembl
        python -m dataload/start entrez
        python -m dataload/start pharmgkb

    '''
    if source not in dataload.__sources_dict__:
        raise ValueError('Unknown source "%s". Should be one of %s' % (source, dataload.__sources_dict__.keys()))

    dataload.__sources__ = dataload.__sources_dict__[source]
    dataload.register_sources()
    dataload.load_all()

def main_test(src):
    import time, random
    for i in range(100+random.randint(0, 50)):
        print src, i
        time.sleep(random.random()+0.5)

def main_test(src):
    import time, random
    t0 = time.time()
    i = 0
    limit = 0 + random.randint(0, 50)
    while True:
        random.random() * random.random()
        j = int(round(time.time()-t0,0))
        if j > i:
            if j > limit:
                break
            else:
                print src, j
                i = j

if __name__ == '__main__':
    main(sys.argv[1])
