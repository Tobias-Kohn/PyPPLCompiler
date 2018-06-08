from pyppl import compile_model_from_file

model = compile_model_from_file("examples/if_model_1.py")
print(model)

print(type(model.get_conditions()))
