import numpy as np
import sys
from ballstick import BallAndStick
from nutil import create_stimulator
from nutil import connect_stimulator_synapse
from collections import namedtuple
from neuron import gui, h
import matplotlib.pyplot as plt
nc_w = 0.02
nc_d = 5
inc_w = 0.02
inc_d = 5
celldim = namedtuple('celldim',"soma_d soma_l dend_d dend_l dend_seg")
cellbiophy = namedtuple('cellbiophy', "Ra, Cm, soma_hh_gnabar, soma_hh_gkbar, soma_hh_gl, soma_hh_el, dend_g, dend_e")
setting = {'geometry': celldim(soma_d=12.6157, soma_l=12.6157, dend_d=1, dend_l=100, dend_seg=101),
                'biophysics': cellbiophy(Ra=100, Cm=1, soma_hh_gnabar=0.12, soma_hh_gkbar=0.036, soma_hh_gl=0.0003, soma_hh_el=-54.3, dend_g=0.001, dend_e=-65)}
N=3

def main(var):
    global nc_w, nc_d, setting, N
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
    esyns = []
    for i in range(N):
        src = cells[i]
        tgt = cells[(i+1)%N]
        syn = h.ExpSyn(tgt.dend(0.5))
        esyns.append(syn)
        nc = h.NetCon(src.soma(0.5)._ref_v, syn, sec=src.soma)
        nc.weight[0] = nc_w # change exitatory to.
        nc.delay = nc_d
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
    h.tstop = 50
    h.run()

    # plot results
    plt.plot(t_vec, soma1_vec, t_vec, soma2_vec, t_vec, soma3_vec)

def main2(var):
    global nc_w, nc_d,setting, N
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
        nc.weight[0] = nc_w # change exitatory to.
        nc.delay = nc_d
        nclist.append(nc)

        syn = h.ExpSyn(tgt.dend(0.5))
        syn.e = -80
        isyns.append(syn)
        inc = h.NetCon(src.soma(0.5)._ref_v, syn, sec=src.soma)
        inc.weight[0] = inc_w # change inhabiton to.
        inc.delay = inc_d
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

if __name__ == '__main__':
   global nc_w, nc_d, inc_w, inc_d
   if len(sys.argv) == 4:
        nc_w = float(sys.argv[3])
   if len(sys.argv) == 5:
        nc_d = float(sys.argv[4])
   if len(sys.argv) == 6:
        inc_w = float(sys.argv[5])
   if len(sys.argv) == 7:
        inc_d = float(sys.argv[6])
   main(sys.argv[1])
   main2(sys.argv[2])

   plt.title("conductance variance1: {} variance2: {}".format(
        sys.argv[1], sys.argv[2]))
   plt.legend(['e_oly_soma1', 'e_oly_soma2', 'e_oly_soma3',
                'e_i_soma1', 'e_i_soma2', 'e_i_soma3'])
   plt.show()

# python C:\Users\ksrir\Development\moose_practice\NEUR634_homework\HW-11\HW_11_e_i.py 0 0