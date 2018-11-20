import numpy as np
from ballstick import BallAndStick
from nutil import create_stimulator
from nutil import connect_stimulator_synapse
from collections import namedtuple
from neuron import gui, h
import matplotlib.pyplot as plt
celldim = namedtuple('celldim',"soma_d soma_l dend_d dend_l dend_seg")
cellbiophy = namedtuple('cellbiophy', "Ra, Cm, soma_hh_gnabar, soma_hh_gkbar, soma_hh_gl, soma_hh_el, dend_g, dend_e")

def main():
    settings = {'geometry': celldim(soma_d=12.6157, soma_l=12.6157, dend_d=1, dend_l=100, dend_seg=101),
                'biophysics': cellbiophy(Ra=100, Cm=1, soma_hh_gnabar=0.12, soma_hh_gkbar=0.036, soma_hh_gl=0.0003, soma_hh_el=-54.3, dend_g=0.001, dend_e=-65)}
    N=3
    cells = [BallAndStick(settings) for i in range(N)]

    nclist = []
    syns = []
    for i in range(N):
        src = cells[i]
        tgt = cells[(i+1)%N]
        syn = h.ExpSyn(tgt.dend(0.5))
        syns.append(syn)
        nc = h.NetCon(src.soma(0.5)._ref_v, syn, sec=src.soma)
        nc.weight[0] = 0.05
        nc.delay = 5
        nclist.append(nc)

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
    h.tstop = 200
    h.run()

    # plot results
    plt.plot(t_vec, soma1_vec, t_vec, soma2_vec, t_vec, soma3_vec)
    plt.legend(['soma1', 'soma2', 'soma3'])
    plt.show()

if __name__ == '__main__':
    import sys
    main()


# python HW_10.py 0 0 0 0.04 0.04 0.04
