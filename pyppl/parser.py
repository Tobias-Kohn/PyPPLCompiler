#
# This file is part of PyPPLCompiler, a compiler for probabilistic programming to create graphical models.
#
# License: GNU GPL 3 (see LICENSE.txt)
#
# 22. Feb 2018, Tobias Kohn
# 02. Jul 2018, Tobias Kohn
#
from typing import Optional

from .transforms import (ppl_new_simplifier, ppl_raw_simplifier, ppl_functions_inliner,
                         ppl_symbol_simplifier, ppl_static_assignments)
from . import ppl_ast
from .fe_clojure import ppl_foppl_parser
from .fe_python import ppl_python_parser
from .backend.ppl_code_generator import generate_code as _gen_code


##### Used for debugging: #####

_print_debug_steps = False

def _print_debug(letter, code):
    if _print_debug_steps:
        print("=" * 30, letter, "=" * 30)
        print(_gen_code(code), flush=True)
        print("-" * 63, flush=True)


def _detect_language(s:str):
    for char in s:
        if char in ['#']:
            return 'py'

        elif char in [';', '(']:
            return 'clj'

        elif 'A' <= char <= 'Z' or 'a' <= char <= 'z' or char == '_':
            return 'py'

        elif char > ' ':
            return 'py'

    return None

##############################


supported_languages = {
    'Python': 'py',
    'Clojure': 'clj',
}


def parse(source:str, *, simplify:bool=True, language:Optional[str]=None, namespace:Optional[dict]=None):
    result = None
    if type(source) is str and str != '':
        lang = _detect_language(source) if language is None else language.lower()
        if lang in ['py', 'python']:
            result = ppl_python_parser.parse(source)

        elif lang in ['clj', 'clojure']:
            result = ppl_foppl_parser.parse(source)

        elif lang == 'foppl':
            result = ppl_foppl_parser.parse(source)

    if type(result) is list:
        result = ppl_ast.makeBody(result)

    if result is not None:
        if namespace is None:
            namespace = {}
        raw_sim = ppl_raw_simplifier.RawSimplifier(namespace)
        result = raw_sim.visit(result)
        _print_debug("A", result)
        if simplify:
            result = ppl_functions_inliner.FunctionInliner().visit(result)
            result = raw_sim.visit(result)
            _print_debug("B", result)

    if simplify and result is not None:
        result = ppl_static_assignments.StaticAssignments().visit(result)
        _print_debug("C", result)
        result = ppl_new_simplifier.Simplifier().visit(result)
        _print_debug("D", result)

    result = ppl_symbol_simplifier.SymbolSimplifier().visit(result)
    _print_debug("E", result)
    return result


def parse_from_file(filename: str, *, simplify:bool=True, language:Optional[str]=None, namespace:Optional[dict]=None):
    with open(filename) as f:
        source = ''.join(f.readlines())
    return parse(source, simplify=simplify, language=language, namespace=namespace)
