import time
import types


#===============================================================================
# Misc. Utility functions
#===============================================================================

def ask(prompt,options='YN'):
    '''Prompt Yes or No,return the upper case 'Y' or 'N'.'''
    options=options.upper()
    while 1:
        s=raw_input(prompt+'[%s]' % '|'.join(list(options))).strip().upper()
        if s in options: break
    return s


def timesofar(t0, clock=0):
    '''return the string(eg.'3m3.42s') for the passed real time/CPU time so far
       from given t0 (return from t0=time.time() for real time/
       t0=time.clock() for CPU time).'''
    if clock:
        t = time.clock() - t0
    else:
        t = time.time() - t0
    h = int(t / 3600)
    m = int((t % 3600) / 60)
    s = round((t % 3600) % 60, 2)
    t_str = ''
    if h != 0:
        t_str += '%sh' % h
    if m != 0:
        t_str += '%sm' % m
    t_str += '%ss' % s
    return t_str



def safe_unicode(s, mask='#'):
    '''replace non-decodable char into "#".'''
    try:
        _s = unicode(s)
    except UnicodeDecodeError, e:
        pos = e.args[2]
        _s = s.replace(s[pos],mask)
        print 'Warning: invalid character "%s" is masked as "%s".' % (s[pos], mask)
        return safe_unicode(_s, mask)

    return _s


def is_int(s):
    """return True or False if input string is integer or not."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def safe_genome_pos(s):
    '''
       >>> safe_genome_pos(1000) = 1000
       >>> safe_genome_pos('1000') = 1000
       >>> safe_genome_pos('10,000') = 100000
    '''
    s_type = type(s)
    if s_type is types.IntType:
        return s
    elif s_type in types.StringTypes:
        return int(s.replace(',',''))
    else:
        raise ValueError('invalid type "%s" for "save_genome_pos"' % s_type)


class dotdict(dict):
    def __getattr__(self, attr):
        value = self.get(attr, None)
        if type(value) is types.DictType:
            return dotdict(value)
        else:
            return value
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__


#===============================================================================
# Misc. Metadata
#===============================================================================
taxid_d = {'human': 9606,
           'mouse': 10090,
           'rat':   10116,
           'fruitfly': 7227,
           'nematode':   6239,
           'zebrafish':   7955,
           'thale-cress':   3702,
           'frog':   8364,
           'pig': 9823,
           }
