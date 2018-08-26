from functools import namedtuple

__all__ = ['cond', 'eq', 'lt', 'gt', 'neq', 'like', 'where']

def cond(*args):
    c = namedtuple('condition', ['op', 'lval', 'rval'])
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

def where(*args):
    return tuple(args)
