#
# This file is part of PyPPLCompiler, a compiler for probabilistic programming to create graphical models.
#
# License: GNU GPL 3 (see LICENSE.txt)
#
# 20. Mar 2018, Tobias Kohn
# 02. Jul 2018, Tobias Kohn
#
from ..ppl_ast import *
from ..aux.ppl_transform_visitor import TransformVisitor
from ..types import ppl_types, ppl_type_inference


class FunctionInliner(TransformVisitor):

    def __init__(self):
        super().__init__()
        self.type_inferencer = ppl_type_inference.TypeInferencer(self)
        self._let_counter = 0

    def get_type(self, node: AstNode):
        result = self.type_inferencer.visit(node)
        return result

    def visit_call(self, node: AstCall):
        if isinstance(node.function, AstSymbol):
            function = self.resolve(node.function.name)
        elif isinstance(node.function, AstFunction):
            function = node.function
        else:
            function = None
        if isinstance(function, AstFunction):
            args = [self.visit(arg) for arg in node.args]
            tmp = generate_temp_var()
            params = function.parameters[:]
            if function.vararg is not None:
                params.append(function.vararg)
            args = function.order_arguments(args, node.keywords)
            arguments = []
            for p, a in zip(params, args):
                if p != '_' and not isinstance(a, AstSymbol):
                    arguments.append(AstDef(p + tmp, a))
                elif not isinstance(a, AstSymbol):
                    arguments.append(a)
            with self.create_scope(tmp):
                for p, a in zip(params, args):
                    if p != '_':
                        if isinstance(a, AstSymbol):
                            self.define(p, a)
                        else:
                            self.define(p, AstSymbol(p + tmp))
                result = self.visit(function.body)

            if isinstance(result, AstReturn):
                return makeBody(arguments, result.value)
                # result = result.value
                # for p, a in zip(reversed(params), reversed(args)):
                #     if p != '_' and not isinstance(a, AstSymbol):
                #         result = AstLet(p + tmp, a, result)
                #     elif not isinstance(a, AstSymbol):
                #         result = makeBody(a, result)
                # return result

            elif isinstance(result, AstBody) and result.last_is_return:
                if len(result) > 1:
                    return makeBody(arguments, result.items[:-1], result.items[-1].value)
                else:
                    return makeBody(arguments, result.items[-1].value)

        return super().visit_call(node)

    def visit_call_map(self, node: AstCall):
        if node.arg_count > 1:
            seq_args = node.args[1:]
            if all([is_vector(arg) for arg in seq_args]) and isinstance(node.args[0], AstSymbol):
                lengths = min([len(arg) for arg in seq_args])
                result = []
                func = node.args[0]
                for i in range(lengths):
                    result.append(AstCall(func, [arg[i] for arg in seq_args]))
                return self.visit(makeVector(result))
            else:
                return self.visit_call(node)
        else:
            return AstVector([])

    def visit_call_zip(self, node: AstCall):
        if node.arg_count > 1:
            seq_args = node.args

            if all([is_vector(arg) for arg in seq_args]):
                lengths = min([len(arg) for arg in seq_args])
                result = []
                for i in range(lengths):
                    result.append(makeVector([arg[i] for arg in seq_args]))
                return self.visit(makeVector(result))
            else:
                arg_types = [self.get_type(arg) for arg in seq_args]
                arg_sizes = [arg.size if isinstance(arg, ppl_types.SequenceType) else None for arg in arg_types]
                if all(arg_sizes):
                    result = []
                    for i in range(min(arg_sizes)):
                        result.append(makeVector([makeSubscript(arg, i) for arg in seq_args]))
                    return self.visit(makeVector(result))

        return self.visit_call(node)

    def visit_def(self, node: AstDef):
        if isinstance(node.value, AstFunction):
            self.define(node.name, node.value, globally=node.global_context)
            return node

        elif not node.global_context:
            tmp = self.scope.name
            if tmp is not None and tmp != '':
                value = self.visit(node.value)
                name = node.name + tmp
                self.define(node.name, AstSymbol(name))
                return node.clone(name=name, value=value)

        else:
            value = self.visit(node.value)
            if isinstance(value, (AstValue, AstValueVector, AstVector)):
                self.define(node.name, value, globally=True)

        return super().visit_def(node)

    def visit_let(self, node: AstLet):
        self._let_counter += 1
        tmp = self.scope.name
        if node.target != '_':
            if tmp is None:
                tmp = '__'
            tmp += 'L{}'.format(self._let_counter)
            source = self.visit(node.source)
            with self.create_scope(tmp):
                self.define(node.target, AstSymbol(node.target + tmp))
                body = self.visit(node.body)
            return AstLet(node.target + tmp, source, body)

        else:
            return super().visit_let(node)

    def visit_symbol(self, node: AstSymbol):
        sym = self.resolve(node.name)
        if isinstance(sym, AstSymbol):
            return sym
        else:
            return node
