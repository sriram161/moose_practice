# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#bash-4.2$ module add python/2.7.15
#bash-4.2$ module add moose

import sys
import moose
import numpy as np
import matplotlib.pyplot as plt
from utilities import create_compartment
from utilities import create_channel
from utilities import compute_comp_area
from utilities import create_output_table
from utilities import plot_vm_table
from utilities import create_set_of_channels
from utilities import copy_connect_channel_moose_paths
from channels_1 import channel_settings

EREST_ACT = -70e-3 #: Resting membrane potential
VMIN = -30e-3 + EREST_ACT
VMAX = 120e-3 + EREST_ACT
VDIVS = 3000
CAMIN = 0
CAMAX = 1
CADIVS = 10E3

def main(experiment_title):
    # Simulation information.
    simtime = 0.1
    simdt = 0.25e-6
    plotdt = 0.25E-3

    # Cell Compartment infromation
    diameter = 30e-6
    length = 50e-6
    Em = EREST_ACT + 10.613e-3
    CM = 1e-6 * 1e4
    RM = 1 /(0.3E-3 * 1e4)

    # Stimulus information
    inj_delay = 20E-3
    inj_amp = 1E-9
    inj_width = 40E-3

    # Create two compartmental model.
    soma = create_compartment('soma', length, diameter, RM, CM, initVM=EREST_ACT, ELEAK=Em)  # Soma creation
    bunch = create_n_dends('dend_', dend_n, 100E-6, 2E-6, soma_RM, soma_CM, soma_RA)         # Dend creation
    for item in bunch.values():
        item.Em = soma.Em
        item.initVm = soma.initVm

    bunch = connect_n_serial(bunch)
    moose.connect(soma, 'axialOut', list(bunch.values())[0], 'handleAxial') # Connect soma and head of dend sequence.

    # Create channels
    channels_set = create_set_of_channels(channel_settings, VDIVS,  VMIN, VMAX, CADIVS, CAMIN, CAMAX)

    moose_paths = [soma.path]
    for channel_name, channel_obj in channels_set.items(): # Copy channels to soma.
        copy_connect_channel_moose_paths(channel_obj, channel_name, moose_paths)

    # Output table.
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    soma_i_table = create_output_table(table_element='/output', table_name='somaIm')
    dend_v_table = create_output_table(table_element='/output', table_name='dendVm')

    # Connect output tables.
    moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    moose.connect(soma_i_table, 'requestOut', pulse_inject, 'getOutputValue')
    moose.connect(dend_v_table, 'requestOut', list(bunch.values())[int(np.median(range(len(bunch))))], 'getVm')

    # Set moose simulation clocks.
    for lable in range(10):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # Plot output tables.
    v_plot = plot_vm_table(simtime, soma_v_table, soma_i_table, dend_v_table title=experiment_title, xlab='Time', ylab='voltage')
    plt.grid(True)
    plt.legend(['v', 'i', 'd'])
    plt.show()

main(experiment_title="Soma voltage")
