import moose
import numpy as np

# Loading different types of morphology file.
pfile = 'layer2.p'
swcfile = 'example.swc'
cell1 = moose.loadModel(pfile, 'neuron')
cell2 = moose.loadModel(swcfile, 'neuron2')

#!module add neuron
from neuron import h
from neuron import gui

dend.nseg = 10
h.topology()

for sec in h.allsec():
     for seg in sec:
         for mech in seg:
             print sec.name(), seg.x, mech.name()

stim = h.IClamp(soma(0.5))
stim.delay=5 # ms
stim.dur = 1  # ms
stim.amp = 0.1

v_vec = h.Vector()
