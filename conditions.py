from functools import namedtuple

def cond(*args):
    c = namedtuple('condition', ['op', 'rval', 'lval'])
    return c(*args)

def eq(*args):
    return cond('=', *args)

def lt(*args):
    return cond('<', *args)

def gt(*args):
    return cond('>', *args)

def neq(*args):
    return cond('!=', *args)

def like(*args):
    return cond('like', *args)
