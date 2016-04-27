import sys
import time
from databuild.builder import DataBuilder, timesofar

def main():
    if len(sys.argv) > 1:
        config = sys.argv[1]
    else:
        config = 'mygene'
        #config = 'mygene_allspecies'
    #use_parallel = '-p' in sys.argv

    t0 = time.time()
    bdr = DataBuilder(backend='es')
    bdr.load_build_config(config)
    #bdr.using_ipython_cluster = use_parallel
    #bdr.target.target_esidxer.number_of_shards = 10   #default 5
    bdr.merge(step=10000)
    print "Finished.", timesofar(t0)


if __name__ == '__main__':
    main()


