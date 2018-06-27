import torch

slope = sample(normal(torch.Tensor(0.0), torch.Tensor(10.0)))
bias  = sample(normal(torch.Tensor(0.0), torch.Tensor(10.0)))
data  = torch.Tensor([[1.0, 2.1], [2.0, 3.9], [3.0, 5.3]])
zn = slope*data[:,0] + bias # y  = mx + c
observe(normal(zn, torch.ones(len(zn))),data[:,1])
[slope, bias]