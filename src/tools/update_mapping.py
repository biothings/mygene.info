import dataload

srcs = []
[srcs.extend(v) for v in dataload.__sources_dict__.values()]
srcs.pop(srcs.index("cpdb"))
srcs.pop(srcs.index("reagent"))
dataload.__sources__ = srcs
dataload.register_sources()
dataload.update_mapping()

