from pyppl import compile_model_from_file

model = compile_model_from_file("examples/gmm_model.py")
print(model)

print("=" * 30)
print(model.code)

# This works only if the necessary modules are installed, i.e. networkx, matplotlib:
model.display_graph()
