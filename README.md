# PyPPLCompiler
A simple compiler to create graphical models out of a subset of Python code. This
compiler is part of the [Pyfo](https://github.com/bradleygramhansen/pyfo)-project.


## Warning

The current project has been used in some limited research projects, but has not yet
been extensively tested. It might not be ready for full production use.


## Basic Usage

The projects requires at least Python 3.4, and has been tested mostly under 
Python 3.6.

In order to compile a model from a program (either Python- or Clojure-based), import
the package and use `compile_model()` or `compile_model_from_file()`, respectively.
The returned object is an instance of the `Model`-class, containing the graphical
model, as well as methods for sampling and computing probabilities according to the
model (see below).

```python
from pyppl import compile_model

my_program = """
x1 = sample(normal(0, 2))
x2 = sample(normal(0, 4))
if x1 > 0:
    observe(normal(x2, 1), 1)
else:
    observe(normal(-1, 1), 1)
"""

model = compile_model(my_program)
print(model)
```

#### Function `compile_model(source, *, language, namespace)`

Takes a program as input, compiles the entire program, produces a Model-class and 
then returns an instance of this class. The input program is provided as a string 
and can be based on Python, Clojure, or basically any language for which there is a 
frontend (function `get_supported_languages()`). If the language is not specified, 
the system tries to detect the language from the the first characters in the 
provided input.

The compiler transforms the provided model into a graphical model and creates a 
`Model`-class, which is based on `base_model` (see module 
[`ppl_base_model.py`](pyppl/ppl_base_model.py)). 
The last step of compilation consists in creating an instance of this Model, which 
is then returned as `model`-object.

The returned model contains, among other field, lists of the vertices (random 
variables) and arcs (edges between the vertices) of the graphical model as 
specified by the input program. Moreover, the methods `gen_prior_samples()` and 
`gen_log_pdf(state)` can be used to sample for the graphical model (returned as a 
'state' dictionary mapping the vertex names to their respective values), and to 
compute the log probability of a given 'state' (mapping of values for each vertex), 
respectively.


### Languages

The system currently supports the following languages as input:
- Python
- Clojure


#### Namespace

During the compilation process, the names of almost all variables are changed, and 
the compilation relies on heavy inlining, eliminating a lot of names. Your input 
language or DSL, however, might contain predefined names, which should either 
remain unaltered, or be mapped to a specific name of function in the output program. 
As an example, you might want to provide a function `select(...)`, which should be 
mapped to `dist.categorical(...)` during compilation. In order to achieve this, 
provide a `namespace` argument to the compile-function like:
```
compile_model(..., namespace = {'select': 'dist.categorical'})
```
If a name should remain unaltered, use `{'name': 'name'}`.



## License

This project is released under the _GNU GPL 3_-license. 
See [LICENSE](LICENSE).


## Contributors
- [Tobias Kohn](https://tobiaskohn.ch)
- [Bradley Gram-Hansen](http://www.robots.ox.ac.uk/~bradley/)

