from __future__ import print_function
import sys
import time
import types
from shlex import shlex

str_types = str if sys.version_info.major == 3 else (str, unicode)


#===============================================================================
# Misc. Utility functions
#===============================================================================

def ask(prompt, options='YN'):
    '''Prompt Yes or No,return the upper case 'Y' or 'N'.'''
    options = options.upper()
    while 1:
        s = raw_input(prompt + '[%s]' % '|'.join(list(options))).strip().upper()
        if s in options:
            break
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
    except UnicodeDecodeError as e:
        pos = e.args[2]
        _s = s.replace(s[pos], mask)
        print('Warning: invalid character "{}" is masked as "{}".'.format(s[pos], mask))
        return safe_unicode(_s, mask)

    return _s


def is_int(s):
    """return True or False if input string is integer or not."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_str(s):
    """return True or False if input is a string or not.
        python3 compatible.
    """
    return isinstance(s, str_types)


def is_seq(li):
    """return True if input is either a list or a tuple.
    """
    return isinstance(li, (list, tuple))


def safe_genome_pos(s):
    '''
       safe_genome_pos(1000) = 1000
       safe_genome_pos('1000') = 1000
       safe_genome_pos('10,000') = 100000
    '''
    if isinstance(s, int):
        return s
    elif isinstance(s, types.StringTypes):
        return int(s.replace(',', ''))
    else:
        raise ValueError('invalid type "%s" for "save_genome_pos"' % type(s))


class dotdict(dict):
    def __getattr__(self, attr):
        value = self.get(attr, None)
        if isinstance(value, dict):
            return dotdict(value)
        else:
            return value
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def split_ids(q):
    '''split input query string into list of ids.
       any of " \t\n\x0b\x0c\r|,+" as the separator,
        but perserving a phrase if quoted
        (either single or double quoted)
        more detailed rules see:
        http://docs.python.org/2/library/shlex.html#parsing-rules

        e.g. split_ids('CDK2 CDK3') --> ['CDK2', 'CDK3']
             split_ids('"CDK2 CDK3"\n CDk4')  --> ['CDK2 CDK3', 'CDK4']

    '''
    lex = shlex(q, posix=True)
    lex.whitespace = ' \t\n\x0b\x0c\r|,+'
    lex.whitespace_split = True
    lex.commenters = ''
    ids = list(lex)
    return ids


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
