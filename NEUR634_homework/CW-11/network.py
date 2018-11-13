import numpy as np
from ballstick import BallAndStick as bs
from neuron import gui
from neuron import h
N = 3
cells = [bs() for i in range(N)]

src = cells[0]
tgt = cells[1]

syn=h.ExpSyn(tgt.dend(0.5))
nc=h.NetCon(src.soma(0.5)._ref_v, syn, sec=src.soma)
nc.weight[0] = .05
nc.delay=5
