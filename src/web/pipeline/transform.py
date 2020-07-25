from biothings.web.pipeline import ESResultTransform

class MygeneTransform(ESResultTransform):
        
    @staticmethod
    def option_sorted(path, obj):
        """
        Sort a container in-place.
        """
        if path == 'homologene.genes':
            return # do not sort this field

        # delegate to super class for normal cases
        ESResultTransform.option_sorted(path, obj)
