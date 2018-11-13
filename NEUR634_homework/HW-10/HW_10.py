# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#bash-4.2$ module add python/2.7.15
#bash-4.2$ module add moose

import sys
import moose
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utilities import create_compartment
from utilities import create_channel
from utilities import compute_comp_area
from utilities import create_output_table
from utilities import plot_vm_table
from utilities import create_set_of_channels
from utilities import copy_connect_channel_moose_paths
from utilities import create_synaptic_channel
from utilities import create_spikegen
from utilities import create_n_dends
from utilities import connect_n_serial
from utilities import copy_syn_channel_moose_paths
from utilities import connect_ca_pool_to_nmda_synapse
from utilities import create_ca_conc_pool
from utilities import copy_ca_pools_moose_paths
from channels_1 import channel_settings
from channels_1 import ca_params
from channels_1 import synapse_settings2 as synapse_settings

EREST_ACT = -70e-3 #: Resting membrane potential
VMIN = -30e-3 + EREST_ACT
VMAX = 120e-3 + EREST_ACT
VDIVS = 3000
CAMIN = 0
CAMAX = 1
CADIVS = 10E3

def main(experiment_title, _rate, _rate2, e_g_max=4E-9, i_g_max=4E-9):
    # Simulation information.
    simtime = 1
    simdt = 0.25e-6
    plotdt = 0.25E-3
    syn_g_max = [4E-9 if g_max == 'na' else np.float(g_max) for g_max in [e_g_max, i_g_max]]
    syn_g_max.append(2E-9)

    # Cell Compartment infromation
    diameter = 30e-6
    length = 50e-6
    Em = EREST_ACT + 10.613e-3
    CM = 1e-6 * 1e4
    RM = 1 /(0.3E-3 * 1e4)
    RA = 4
    dend_n = 5

    # Create two compartmental model.
    soma = create_compartment('soma', length, diameter, RM, CM, initVM=EREST_ACT, ELEAK=Em)  # Soma creation
    bunch = create_n_dends('dend_', dend_n, length, diameter, RM, CM, RA)         # Dend creation
    for item in bunch.values():
        item.Em = Em
        item.initVm = EREST_ACT

    bunch = connect_n_serial(bunch)
    moose.connect( soma, 'axial', list(bunch.values())[0], 'raxial' )

    # Create channels
    channels_set = create_set_of_channels(channel_settings, VDIVS,  VMIN, VMAX, CADIVS, CAMIN, CAMAX)

    # Create calcium pools in library.
    ca_pool = create_ca_conc_pool(ca_params)

    # Create synaptic channel
    synapses_and_handles = [create_synaptic_channel(setting.syn_name, g_max, setting.tau1,
                        setting.tau2, setting.ek, setting.synapse_count, setting.delay, setting.params) for setting, g_max in zip(synapse_settings, syn_g_max)]

    # Copy the synaptic channels to moose compartments.
    moose_paths = [moose.element('/dend_2').path]
    for syn, syn_handle in synapses_and_handles:
        copy_syn_channel_moose_paths(syn, syn.name, moose_paths)

    # copy calcium pools to all compartments.
    copy_ca_pools_moose_paths(ca_pool, 'CaPool', moose_paths)

    # create pre-synaptic input
    spikegen_1 = create_spikegen(name='spikegen_1', type='random', refractory_period=1E-3, rate=_rate)
    spikegen_2 = create_spikegen(name='spikegen_2', type='random', refractory_period=1E-3, rate=_rate2)

    # Connect spike generator to synapses.
    moose.connect(spikegen_1, 'spikeOut', moose.element('/dend_2[0]/syn[0]/synhandler').synapse[0], 'addSpike')
    moose.connect(spikegen_2, 'spikeOut', moose.element('/dend_2[0]/syn2[0]/synhandler').synapse[0], 'addSpike')

    # Connect NMDA receptor channels to calcium pools.
    connect_ca_pool_to_nmda_synapse(moose_paths, 'CaPool')

    # connect channels to compartments.
    for channel_name, channel_obj in channels_set.items(): # Copy channels to soma.
        copy_connect_channel_moose_paths(channel_obj, channel_name, moose_paths)

    # Output table.
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    dend1_v_table = create_output_table(table_element='/output', table_name='dend1Vm')
    # Connect output tables.
    moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    moose.connect(dend1_v_table, 'requestOut', moose.element('/dend_2'), 'getVm')

    # Set moose simulation clocks.
    for lable in range(10):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # Plot output tables.
    v_plot = plot_vm_table(simtime, soma_v_table, dend1_v_table, title=experiment_title.format(_rate, _rate2, syn_g_max[0], syn_g_max[1]), xlab='Time', ylab='voltage')
    plt.grid(True)
    plt.legend(['soma', 'dend'])
    plt.savefig('graph.png')

main(experiment_title="Membrane potential exitation(rate, g_max): ({0}Hz, {2}S) Inhabition(rate, g_max): ({1}Hz, {3}S)", _rate=sys.argv[1], _rate2 = sys.argv[2], e_g_max=sys.argv[3], i_g_max=sys.argv[4])

# python3 HW_10.py 10 10 na na
