from pyppl import compile_model_from_file

model = compile_model_from_file("examples/hmm_model_map_1.clj")
print(model)

# This works only if the necessary modules are installed, i.e. networkx, matplotlib:
model.display_graph()
