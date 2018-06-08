#
# This file is part of PyPPLCompiler, a compiler for probabilistic programming to create graphical models.
#
# License: GNU GPL 3 (see LICENSE.txt)
#
# 19. Feb 2018, Tobias Kohn
# 19. Feb 2018, Tobias Kohn
#
from .ppl_types import *

#######################################################################################################################

def _binary_(left, right):
    return union(left, right)

def add(left, right):
    return _binary_(left, right)

def sub(left, right):
    return _binary_(left, right)

def mul(left, right):
    if left in String and right in Integer:
        return left
    elif left in Integer and right in String:
        return right
    return _binary_(left, right)

def div(left, right):
    return _binary_(left, right)

def idiv(left, right):
    return _binary_(left, right)

def mod(left, right):
    return _binary_(left, right)


#######################################################################################################################

def neg(item):
    return item

def pos(item):
    return item
