import numpy as np
from ballstick import BallAndStick
from nutil import create_stimulator
from nutil import connect_stimulator_synapse
from collections import namedtuple
from neuron import gui, h
import matplotlib.pyplot as plt
celldim = namedtuple('celldim',"soma_d soma_l dend_d dend_l dend_seg")
cellbiophy = namedtuple('cellbiophy', "Ra, Cm, soma_hh_gnabar, soma_hh_gkbar, soma_hh_gl, soma_hh_el, dend_g, dend_e")

def main(var):
    setting = {'geometry': celldim(soma_d=12.6157, soma_l=12.6157, dend_d=1, dend_l=100, dend_seg=101),
                'biophysics': cellbiophy(Ra=100, Cm=1, soma_hh_gnabar=0.12, soma_hh_gkbar=0.036, soma_hh_gl=0.0003, soma_hh_el=-54.3, dend_g=0.001, dend_e=-65)}
    N=3
    var = np.float(var)
    deviation = lambda r: np.random.standard_normal(N)*r
    cell_settings = []
    for i in range(N):
        set = {}
        set['geometry'] = celldim(soma_d=12.6157, soma_l=12.6157, dend_d=1, dend_l=100, dend_seg=101)
        set['biophysics'] = cellbiophy(Ra=100, Cm=1, soma_hh_gnabar=0.12 + 0.12*deviation(var)[i],
                            soma_hh_gkbar=0.036 + 0.036*deviation(var)[i], soma_hh_gl= 0.0003 + 0.0003*deviation(var)[i],
                            soma_hh_el=-54.3, dend_g=0.001, dend_e=-65)
        cell_settings.append(set)

    cells = [BallAndStick(settings) for settings in cell_settings]

    nclist = []
    inclist = []
    esyns = []
    isyns = []
    for i in range(N):
        src = cells[i]
        tgt = cells[(i+1)%N]
        syn = h.ExpSyn(tgt.dend(0.5))
        esyns.append(syn)
        nc = h.NetCon(src.soma(0.5)._ref_v, syn, sec=src.soma)
        nc.weight[0] = 0.02 # change exitatory to.
        nc.delay = 5
        nclist.append(nc)

        syn = h.ExpSyn(tgt.dend(0.5))
        syn.e = -80
        isyns.append(syn)
        nc = h.NetCon(src.soma(0.5)._ref_v, syn, sec=src.soma)
        nc.weight[0] = 0.02 # change inhabiton to.
        nc.delay = 5
        inclist.append(nc)

    # Create AlphaSynapse for init network
    syn = h.AlphaSynapse(cells[0].dend(0.5))
    syn.gmax = 0.1
    syn.tau = 1
    syn.onset = 20
    syn.e = 0

    # Create output tables
    t_vec = h.Vector()
    soma1_vec = h.Vector()
    soma2_vec = h.Vector()
    soma3_vec = h.Vector()
    t_vec.record(h._ref_t)
    soma1_vec.record(cells[0].soma(0.5)._ref_v)
    soma2_vec.record(cells[1].soma(0.5)._ref_v)
    soma3_vec.record(cells[2].soma(0.5)._ref_v)

    # Run simulation
    h.tstop = 50
    h.run()

    # plot results
    plt.plot(t_vec, soma1_vec, t_vec, soma2_vec, t_vec, soma3_vec)
    plt.legend(['soma1', 'soma2', 'soma3'])
    plt.show()

if __name__ == '__main__':
    import sys
    main(sys.argv[1])

# python HW_11.py 0
