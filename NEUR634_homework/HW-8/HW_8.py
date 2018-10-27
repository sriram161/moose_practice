from neuron import gui, h
from matplotlib import pyplot as plt

soma = h.Section(name='soma')
dend = h.Section(name='dend')
for sec in h.allsec():
    sec.Ra = 4
    sec.cm = 1

soma.L = 50
soma.diam = 30
soma.insert('hh')
soma.gnabar_hh = 0.12
soma.gkbar_hh = 0.036
soma.gl_hh = 0.0003
soma.el_hh = -54.3

dend.L = 50
dend.diam = 30
dend.g_pas = 0.0003
dend.e_pas = -70
dend.insert('hh')
dend.gkbar_hh = 0.05 # Your channel conductance. # try 0, 0.05 and 0.5
dend.gl_hh = 0.0003
dend.el_hh = -54.3

# Connect soma and dendrite
dend.connect(soma(1.0))

# stimulation at dend
stim = h.IClamp(dend(1.0))
stim.amp = 0.3 # Try variations 0, 0.003, 0.03, 0.3 and 3.
stim.delay = 40
stim.dur = 1

# recordings
t_vec = h.Vector()
v_vec_soma = h.Vector()
v_vec_dend = h.Vector()
v_vec_soma.record(soma(1.0)._ref_v)
v_vec_dend.record(dend(1.0)._ref_v)
t_vec.record(h._ref_t)

h.tstop = 60
h.run()

plt.plot(t_vec, v_vec_soma, t_vec, v_vec_dend, 'r')
plt.xlabel('time ms')
plt.ylabel('voltage mV')
plt.show()


# g_pas for membrane = 0.0003
# e_pas for membrane = -70
# Ra for membrane = 4
# cm for membrane = 1
# soma length = 50
# soma diameter = 30
