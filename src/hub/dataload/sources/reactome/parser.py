import os.path
from biothings.utils.dataload import tab2dict_iter

def load_data(data_folder):
    datafile = os.path.join(data_folder, 'NCBI2Reactome.txt')
    data = tab2dict_iter(datafile, (0, 1, 3), 0, header=0, alwayslist=True)
    def convert(data):
        for dvalue in data:
            assert len(dvalue) == 1
            _id = list(dvalue.keys())[0]
            doc = {"_id" : _id,
                   "pathway" : {"reactome" : None}
                  }
            lvals = []
            for val in dvalue[_id]:
                lvals.append({"id" : val[0], "name" : val[1]})
            if len(lvals) == 1:
                lvals = lvals.pop()
            doc["pathway"]["reactome"] = lvals
            yield doc

    return convert(data)
