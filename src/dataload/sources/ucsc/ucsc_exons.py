from .ucsc_base import load_ucsc_exons
import biothings.dataload.uploader as uploader


class UCSCExonsUploader(uploader.MergerSourceUploader):

    name = "ucsc_exons"
    main_source = "ucsc"

    def load_data(self,data_folder):
    	genedoc_d = load_ucsc_exons(data_folder)
    	return genedoc_d

    def get_mapping(self):
	    mapping = {
	        #do not index exons
	        "exons":  {
	            "type": "object",
	            "enabled": False
	        },
	        #do not index exons_hg19
	        "exons_hg19":  {
	            "type": "object",
	            "enabled": False
	        },
	        "exons_mm9":  {
	            "type": "object",
	            "enabled": False
	        }
	    }
	    return mapping


