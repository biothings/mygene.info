import json


def make_object(attr, value):
    '''
    make_object('a.b.c', 100) -->
    or make_object(['a','b','c'], 100) -->
      {a:{b:{c:100}}}
    '''
    attr_list = attr.split('.')
    s = ''
    for k in attr_list:
        s += '{"' + k + '":'
    s += json.dumps(value)
    s += "}" * (len(attr_list))
    return json.loads(s)


def merge_object(obj1, obj2):
    for k in obj2:
        try:
            if isinstance(obj2[k], dict):
                obj1[k] = merge_object(obj1[k], obj2[k])
            else:
                obj1[k] = obj2[k]
        except:
            obj1[k] = obj2[k]
    return obj1


def parse_dot_fields(genedoc):
    """
    parse_dot_fields({'a': 1, 'b.c': 2, 'b.a.c': 3})
     should return
        {'a': 1, 'b': {'a': {'c': 3}, 'c': 2}}
    """
    dot_fields = []
    expanded_doc = {}
    for key in genedoc:
        if key.find('.') != -1:
            dot_fields.append(key)
            expanded_doc = merge_object(expanded_doc, make_object(key, genedoc[key]))
    genedoc.update(expanded_doc)
    for key in dot_fields:
        del genedoc[key]
    return genedoc


def compose_dot_fields_by_fields(genedoc, fields):
    """
    reverse funtion of parse_dot_fields
    """
    res = None
    to_del = set()
    for k in fields:
        if k.find('.') != -1:
            if not res:
                import copy
                res = copy.deepcopy(genedoc)
            ks = k.split('.')
            broke = False
            if ks[0] in genedoc:
                t = genedoc[ks[0]]
                for e in ks[1:]:
                    if e in t:
                        t = t[e]
                    else:
                        broke = True
                        break
                if broke:
                    continue
                to_del.add(ks[0])
                res[k] = t

    for k in to_del:
        del res[k]

    return res if res else genedoc
