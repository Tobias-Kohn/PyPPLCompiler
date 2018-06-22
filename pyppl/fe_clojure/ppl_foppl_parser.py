#
# This file is part of PyPPLCompiler, a compiler for probabilistic programming to create graphical models.
#
# License: GNU GPL 3 (see LICENSE.txt)
#
# 21. Feb 2018, Tobias Kohn
# 22. Jun 2018, Tobias Kohn
#
from ..fe_clojure import ppl_clojure_forms as clj
from ..ppl_ast import *
from .ppl_clojure_lexer import ClojureLexer
from .ppl_clojure_parser import ClojureParser


#######################################################################################################################

class FopplParser(ClojureParser):

    def visit_loop(self, count, initial_data, function, *args):
        if isinstance(count, clj.Symbol):
            count = self.value_bindings.get(count.name, None)
            if type(count) is not int:
                raise SyntaxError("loop requires an integer value as first argument")
        elif clj.is_integer(count):
            count = count.value
        else:
            raise SyntaxError("loop requires an integer value as first argument")
        initial_data = initial_data.visit(self)
        function = function.visit(self)
        args = [arg.visit(self) for arg in args]
        result = initial_data
        i = 0
        while i < count:
            result = AstCall(function, [AstValue(i), result] + args)
            i += 1
        return result


#######################################################################################################################

def parse(source):
    clj_ast = list(ClojureLexer(source))
    ppl_ast = FopplParser().visit(clj_ast)
    return ppl_ast
