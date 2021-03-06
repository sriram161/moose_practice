# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#bash-4.2$ module add python/2.7.15
#bash-4.2$ module add moose

import moose
import matplotlib.pyplot as plt
from utilities import create_channel
from utilities import create_swc_model
from utilities import create_pulse_generator
from utilities import compute_comp_area
from utilities import create_output_table
from utilities import plot_vm_table
from utilities import create_set_of_channels
from utilities import copy_connect_channel_moose_paths
from collections import namedtuple
from channels_3 import channel_settings

EREST_ACT = -70e-3 #: Resting membrane potential
VMIN = -30e-3 + EREST_ACT
VMAX = 120e-3 + EREST_ACT
VDIVS = 3000


def main():
    # Simulation information.
    simtime = 0.1
    simdt = 0.25e-5
    plotdt = 0.25e-3

    # Cell Compartment infromation
    diameter = 30e-6
    length = 50e-6
    Em = EREST_ACT + 10.613e-3
    CM = 1e-6 * 1e4
    RM = 1 /(0.3E-3 * 1e4)
    RA = 4

    # Stimulus information
    inj_delay = 20E-3
    inj_amp = 1E-9
    inj_width = 40E-3

    # Create cell
    chicken_model = create_swc_model(root_name='E19', file_name='E19-cell_filling-caudal.CNG.swc', RM=RM, CM=CM, RA=RA, ELEAK=Em, initVM=Em)
    soma = moose.element('/E19[0]/soma')

    # Create channels
    channels_set = create_set_of_channels(channel_settings, VDIVS,  VMIN, VMAX)

    # Fetch all compartment paths.
    moose_paths = []
    for comp in moose.wildcardFind(chicken_model.path+'/#[TYPE=Compartment]'):
        moose_paths.append(comp.path)

    # Copy all channels to compartments.
    for channel_name, channel_obj in channels_set.items():
        copy_connect_channel_moose_paths(channel_obj, channel_name, moose_paths)

    # connect pulse gen
    pulse_inject = create_pulse_generator(soma, inj_width, inj_amp, delay=inj_delay)

    # Output table
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    soma_i_table = create_output_table(table_element='/output', table_name='somaIm')
    chicken_dend_table = create_output_table(table_element='/output', table_name='chkdend')

    # Connect output tables
    moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    moose.connect(soma_i_table, 'requestOut', pulse_inject, 'getOutputValue')
    moose.connect(chicken_dend_table, 'requestOut', moose.element('/E19[0]/dend_36_0'), 'getVm')

    # Set moose simulation clocks
    for lable in range(7):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # Plot output tables.
    v_plot = plot_vm_table(simtime, soma_v_table, soma_i_table, chicken_dend_table, title="soma vs dend new k1 chan g_bar = 0.05")
    v_plot.legend(['soma_v', 'i', 'dend_v'])
    plt.grid(True)
    plt.show()

main()
