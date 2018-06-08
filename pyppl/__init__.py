#
# This file is part of PyPPLCompiler, a compiler for probabilistic programming to create graphical models.
#
# License: GNU GPL 3 (see LICENSE.txt)
#
# 07. Feb 2018, Tobias Kohn
# 08. Jun 2018, Tobias Kohn
#

from typing import Optional
from . import distributions, parser
from .backend import ppl_graph_generator

def get_supported_languages():
    """
    Returns the list of input languages currently supported by the system. The returned value is a set of strings,
    where each string is the name of language, such as `{'Python', 'Clojure'}`.

    :return:  A set of strings with languages currently supported by the compiler.
    """
    return set(parser.supported_languages.keys())


def compile_model(source, *,
                  language: Optional[str]=None,
                  imports=None,
                  base_class: Optional[str]=None,
                  namespace: Optional[dict]=None):
    """
    COMPILE_MODEL
    =============
        Takes a program as input, compiles the entire program, produces a Model-class and then returns an instance of
        this class. The input program is provided as a string and can be based on Python, Clojure, or basically any
        language for which there is a frontend (see function `get_supported_languages()`). If the language is not
        specified, the system tries to detect the language from the the first characters in the provided input.

        The compiler transforms the provided model into a graphical model and creates a `Model`-class, which is based
        on `base_model` (see module `ppl_base_model.py`). The last step of compilation consists in creating an instance
        of this Model, which is then returned as `model`-object.

        The returned model contains, among other field, lists of the vertices (random variables) and arcs (edges
        between the vertices) of the graphical model as specified by the input program. Moreover, the methods
        `gen_prior_samples()` and `gen_log_pdf(state)` can be used to sample for the graphical model (returned as
        a 'state' dictionary mapping the vertex names to their respective values), and to compute the log probability
        of a given 'state' (mapping of values for each vertex), respectively.

    Namespace
    ---------
        During the compilation process, the names of almost all variables are changed, and the compilation relies on
        heavy inlining, eliminating a lot of names. Your input language or DSL, however, might contain predefined names,
        which should either remain unaltered, or be mapped to a specific name of function in the output program. As an
        example, you might want to provide a function `select(...)`, which should be mapped to `dist.categorical(...)`
        during compilation. In order to achieve this, provide a `namespace` argument to the compile-function like:
        ```
        compile_model(..., namespace = {'select': 'dist.categorical'})
        ```
        If a name should remain unaltered, use `{'name': 'name'}`.

    :param source:      A string containing the source code to be compiled.
    :param language:    [Optional] The language of the source code as a string like `Python`, `py` or `clj`.
    :param imports:     [Optional] A list or tuple of strings, giving the names of modules to import.
    :param base_class:  [Optional] The string of a base class upon which the model should be based.
    :param namespace:   [Optional] A dictionary with predefined names and their mapping for the output.
    :return:            An instance of the `Model` class.
    """
    if type(imports) in (list, set, tuple):
        imports = '\n'.join(imports)
    if namespace is not None:
        ns = distributions.namespace.copy()
        ns.update(namespace)
        namespace = ns
    else:
        namespace = distributions.namespace
    ast = parser.parse(source, language=language, namespace=namespace)
    gg = ppl_graph_generator.GraphGenerator()
    gg.visit(ast)
    return gg.generate_model(base_class=base_class, imports=imports)


def compile_model_from_file(filename: str, *,
                            language: Optional[str]=None,
                            imports=None,
                            base_class: Optional[str]=None,
                            namespace: Optional[dict]=None):
    """
    Takes a program as input and returns a graphical model of the program. In contrast to `compile_model`, the input
    is the name of file to be loaded rather than the program itself.

    :param filename:    The name of an input file as string.
    :param language:    [Optional] The language of the source code as a string like `Python`, `py` or `clj`.
    :param imports:     [Optional] A list or tuple of strings, giving the names of modules to import.
    :param base_class:  [Optional] The string of a base class upon which the model should be based.
    :param namespace:   [Optional] A dictionary with predefined names and their mapping for the output.
    :return:            An instance of the `Model` class.
    """
    with open(filename) as f:
        lines = ''.join(f.readlines())
        return compile_model(lines, language=language, imports=imports, base_class=base_class,
                             namespace=namespace)
