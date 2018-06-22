from pyppl import compile_model_from_file

model = compile_model_from_file("examples/if_model_1.py")
print(model)

print("=" * 30)
print(model.code)

# This works only if the necessary modules are installed, i.e. networkx, matplotlib:
model.display_graph()
