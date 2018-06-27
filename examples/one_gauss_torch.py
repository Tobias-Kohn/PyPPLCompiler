import torch
n = 2
x = sample(normal(3*torch.ones(n), 5*torch.ones(n)))
y = x + 1
observations = 7*torch.ones(n)
observe(normal(y, 2*torch.ones(n)), observations)
y