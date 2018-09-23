from neuron import h
from neuron import gui
import matplotlib.pyplot as plt

# Soma createion
soma = h.Section(name = 'soma')
soma.diam = 25
soma.L = 50
soma.insert('pas')
soma.pas.g = 0.002

# Dend creation
dend = h.Section(name = 'dend')
dend.diam = soma.diam
dend.L = soma.L
dend.insert('pas')
dend.pas.g = 0.002

# connect soma with dend.
dend.connect(soma(1))
# Split dend into 101 segments.
dend.nseg = 101

# Stimulation at soma.
stim = h.IClamp(soma(0.5))
stim.delay = 5
stim.dur = 1
stim.amp = 0.1

# Output tables
soma_vec = h.Vector()
time_vec = h.Vector()
dend_vec = h.Vector()

soma_vec.record(soma(0.5)._ref_V)
time_vec.record(h._ref_t)
dend_vec.record(dend(0.5)._ref_v) #??

h.tstop = 40
h.run()

plt.plot(time_vec, soma_vec, time_vec, dend_vec, title="Neuron soma and dend space descitization")
plt.legend(['soma', 'dend'])
plt.grid(True)
plt.show()
