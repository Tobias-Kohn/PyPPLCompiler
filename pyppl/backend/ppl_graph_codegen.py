#
# This file is part of PyPPLCompiler, a compiler for probabilistic programming to create graphical models.
#
# License: GNU GPL 3 (see LICENSE.txt)
#
# 12. Mar 2018, Tobias Kohn
# 27. Jun 2018, Tobias Kohn
#
import datetime
import importlib
from ..graphs import *
from ..ppl_ast import *


class GraphCodeGenerator(object):
    """
    In contrast to the more general code generator `CodeGenerator`, this class creates the code for a graph-based
    model. The output of the method `generate_model_code()` is therefore the code of a class `Model` with functions
    such as `gen_log_pdf()` or `gen_prior_samples()`, including all necessary imports.

    You want to change this class if you need additional (or adapted) methods in your model-class.

    Usage:
      ```
      graph = ...   # <- actually generated by the graph-factory/generator
      graph_code_gen = GraphCodeGenerator(graph.nodes, state_object='state', imports='import distributions as dist')
      code = graph_code_gen.generate_model_code()
      my_globals = {}
      exec(code, my_globals)
      Model = my_globals['Model']
      model = Model(graph.vertices, graph.arcs, graph.data, graph.conditionals)
      ```
      The state-object specifies the actual name of the dictionary/map that holds the state, i. e. all the variables.
      When any state-object is given, the generated code reads, say, `state['x']` instead of purely `x`.

    Hacking:
      The `generate_model_code`-method uses three fixed methods to generate the code for `__init__`, `__repr__` as
      well as the doc-string: `_generate_doc_string`, `_generate_init_method`, `_generate_repr_method`. After that,
      it scans the object instance of `GraphCodeGenerator` for public methods, and assumes that each method returns
      the code for the respective method.

      Say, for instance, you wanted your Model-class to have a method `get_all_nodes` with the following code:
      ```
      def get_all_nodes(self):
          return set.union(self.vertices, self.conditionals)
      ```
      You then add the following method to the `GraphCodeGenerator` and be done.
      ```
      def get_all_nodes(self):
          return "return set.union(self.vertices, self.conditionals)"
      ```
      If, on the other hand, you need some additional parameters/arguments for your method, then you should return
      a tuple with the first element being the parameters as a string, and the second element being the code as before.
      ```
      def get_all_nodes(self):
          return "param1, param2", "return set.union(self.vertices, self.conditionals)"
      ```

      Of course, you do not need to actually change this class, but you can derive a new class from it, if you wish.
    """

    def __init__(self, nodes: list, state_object: Optional[str]=None, imports: Optional[str]=None):
        self.nodes = nodes
        self.state_object = state_object
        self.imports = imports
        self.bit_vector_name = None
        self.logpdf_suffix = None

    def _complete_imports(self, imports: str):
        if imports != '':
            has_dist = False
            uses_numpy = False
            uses_torch = False
            for s in imports.split('\n'):
                s = s.strip()
                if s.endswith(' dist') or s.endswith('.dist'):
                    has_dist = True
                if s.startswith('from'):
                    s = s[5:]
                elif s.startswith('import'):
                    s = s[7:]
                i = 0
                while i < len(s) and 'A' <= s[i].upper() <= 'Z':
                    i += 1
                m = s[:i]
                uses_numpy = uses_numpy or m == 'numpy'
                uses_torch = uses_torch or m == 'torch'
            if uses_torch or uses_numpy:
                self.logpdf_suffix = ''
            if not has_dist:
                if uses_torch:
                    try:
                        __import__("pyfo.distributions")
                        return 'import pyfo.distributions as dist\n'
                    except ModuleNotFoundError:
                        return 'import torch.distributions as dist\n'
        return ''


    def generate_model_code(self, *,
                            class_name: str='Model',
                            base_class: str='',
                            imports: str='') -> str:

        if self.imports is not None:
            imports = self.imports + "\n" + imports
        if base_class is None:
            base_class = ''

        if '.' in base_class:
            idx = base_class.rindex('.')
            base_module = base_class[:idx]
            try:
                importlib.import_module(base_module)
                base_class = base_class[idx+1:]
                imports = "from {} import {}\n".format(base_module, base_class) + imports
            except:
                pass

        try:
            graph_module = 'pyppl.aux.graph_plots'
            m = importlib.import_module(graph_module)
            names = [n for n in dir(m) if not n.startswith('_')]
            if len(names) > 1:
                names = [n for n in names if n[0].isupper()]
            if len(names) == 1:
                if base_class != '':
                    base_class += ', '
                base_class += '_' + names[0]
                imports = "from {} import {} as _{}\n".format(graph_module, names[0], names[0]) + imports
        except ModuleNotFoundError:
            pass

        imports = self._complete_imports(imports) + imports

        result = ["# {}".format(datetime.datetime.now()),
                  imports,
                  "class {}({}):".format(class_name, base_class)]

        doc_str = self._generate_doc_string()
        if doc_str is not None and doc_str != '':
            result.append('\t"""\n\t{}\n\t"""'.format(doc_str.replace('\n', '\n\t')))
        result.append('')

        init_method = self._generate_init_method()
        if init_method is not None:
            result.append('\t' + init_method.replace('\n', '\n\t'))

        repr_method = self._generate_repr_method()
        if repr_method is not None:
            result.append('\t' + repr_method.replace('\n', '\n\t'))

        methods = [x for x in dir(self) if not x.startswith('_') and x != 'generate_model_code']
        for method_name in methods:
            method = getattr(self, method_name)
            if callable(method):
                code = method()
                if type(code) is tuple and len(code) == 2:
                    args, code = code
                    args = 'self, ' + args
                else:
                    args = 'self'
                code = code.replace('\n', '\n\t\t')
                result.append("\tdef {}({}):\n\t\t{}\n".format(method_name, args, code))

        return '\n'.join(result)

    def _generate_doc_string(self):
        return ''

    def _generate_init_method(self):
        return "def __init__(self, vertices: set, arcs: set, data: set, conditionals: set):\n" \
               "\tsuper().__init__()\n" \
               "\tself.vertices = vertices\n" \
               "\tself.arcs = arcs\n" \
               "\tself.data = data\n" \
               "\tself.conditionals = conditionals\n"

    def _generate_repr_method(self):
        s = "def __repr__(self):\n" \
            "\tV = '\\n'.join(sorted([repr(v) for v in self.vertices]))\n" \
            "\tA = ', '.join(['({}, {})'.format(u.name, v.name) for (u, v) in self.arcs]) if len(self.arcs) > 0 else '  -'\n" \
            "\tC = '\\n'.join(sorted([repr(v) for v in self.conditionals])) if len(self.conditionals) > 0 else '  -'\n" \
            "\tD = '\\n'.join([repr(u) for u in self.data]) if len(self.data) > 0 else '  -'\n" \
            "\tgraph = 'Vertices V:\\n{V}\\nArcs A:\\n  {A}\\n\\nConditions C:\\n{C}\\n\\nData D:\\n{D}\\n'.format(V=V, A=A, C=C, D=D)\n" \
            "\tgraph = '#Vertices: {}, #Arcs: {}\\n'.format(len(self.vertices), len(self.arcs)) + graph\n" \
            "\treturn graph\n"
        return s

    def get_vertices(self):
        return "return self.vertices"

    def get_vertices_names(self):
        return "return [v.name for v in self.vertices]"

    def get_arcs(self):
        return "return self.arcs"

    def get_arcs_names(self):
        return "return [(u.name, v.name) for (u, v) in self.arcs]"

    def get_conditions(self):
        return "return self.conditionals"

    def gen_cond_vars(self):
        return "return [c.name for c in self.conditionals]"

    def gen_if_vars(self):
        return "return [v.name for v in self.vertices if v.is_conditional and v.is_sampled and v.is_continuous]"

    def gen_cont_vars(self):
        return "return [v.name for v in self.vertices if v.is_continuous and not v.is_conditional and v.is_sampled]"

    def gen_disc_vars(self):
        return "return [v.name for v in self.vertices if v.is_discrete and v.is_sampled]"

    def get_vars(self):
        return "return [v.name for v in self.vertices if v.is_sampled]"

    def _gen_code(self, buffer: list, code_for_vertex, *, want_data_node: bool=True, flags=None):
        distribution = None
        state = self.state_object
        if self.bit_vector_name is not None:
            if state is not None:
                buffer.append("{}['{}'] = 0".format(state, self.bit_vector_name))
            else:
                buffer.append("{} = 0".format(self.bit_vector_name))
        for node in self.nodes:
            name = node.name
            if state is not None:
                name = "{}['{}']".format(state, name)
            if isinstance(node, Vertex):
                if flags is not None:
                    code = "dst_ = {}".format(node.get_code(**flags))
                else:
                    code = "dst_ = {}".format(node.get_code())
                if code != distribution:
                    buffer.append(code)
                    distribution = code
                code = code_for_vertex(name, node)
                if type(code) is str:
                    buffer.append(code)
                elif type(code) is list:
                    buffer += code

            elif isinstance(node, ConditionNode) and self.bit_vector_name is not None:
                bit_vector = "{}['{}']".format(state, self.bit_vector_name) if state is not None else self.bit_vector_name
                code = "_c = {}\n{} = _c".format(node.get_code(), name)
                buffer.append(code)
                buffer.append("{} |= {} if _c else 0".format(bit_vector, node.bit_index))

            elif want_data_node or not isinstance(node, DataNode):
                code = "{} = {}".format(name, node.get_code())
                buffer.append(code)

    def gen_log_pdf(self):
        def code_for_vertex(name: str, node: Vertex):
            cond_code = node.get_cond_code(state_object=self.state_object)
            if cond_code is not None:
                result = cond_code + "log_pdf = log_pdf + dst_.log_pdf({})".format(name)
            else:
                result = "log_pdf = log_pdf + dst_.log_pdf({})".format(name)
            if self.logpdf_suffix is not None:
                result = result + self.logpdf_suffix
            return result

        logpdf_code = ["log_pdf = 0"]
        self._gen_code(logpdf_code, code_for_vertex=code_for_vertex, want_data_node=False)
        logpdf_code.append("return log_pdf")
        return 'state', '\n'.join(logpdf_code)

    def gen_log_pdf_transformed(self):
        def code_for_vertex(name: str, node: Vertex):
            cond_code = node.get_cond_code(state_object=self.state_object)
            if cond_code is not None:
                result = cond_code + "log_pdf = log_pdf + dst_.log_pdf({})".format(name)
            else:
                result = "log_pdf = log_pdf + dst_.log_pdf({})".format(name)
            if self.logpdf_suffix is not None:
                result += self.logpdf_suffix
            return result
        # Note to self : To change suffix for torch or numpy look at line 87-88 in compiled imports (above)
        logpdf_code = ["log_pdf = 0"]
        self._gen_code(logpdf_code, code_for_vertex=code_for_vertex, want_data_node=False, flags={'transformed': True})
        logpdf_code.append("return log_pdf.sum()")
        return 'state', '\n'.join(logpdf_code)

    def gen_prior_samples(self):

        def code_for_vertex(name: str, node: Vertex):
            if node.has_observation:
                return "{} = {}".format(name, node.observation)
            sample_size = node.sample_size
            if sample_size is not None and sample_size > 1:
                return "{} = dst_.sample(sample_size={})".format(name, sample_size)
            else:
                return "{} = dst_.sample()".format(name)

        state = self.state_object
        sample_code = []
        if state is not None:
            sample_code.append(state + " = {}")
        self._gen_code(sample_code, code_for_vertex=code_for_vertex, want_data_node=True)
        if state is not None:
            sample_code.append("return " + state)
        return '\n'.join(sample_code)

    def gen_cond_bit_vector(self):
        code = "result = 0\n" \
               "for cond in self.conditionals:\n" \
               "\tresult = cond.update_bit_vector(state, result)\n" \
               "return result"
        return 'state', code

