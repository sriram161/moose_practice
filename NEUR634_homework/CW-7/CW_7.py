# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#bash-4.2$ module add python/2.7.15
#bash-4.2$ module add moose

import moose
import matplotlib.pyplot as plt
from utilities import create_compartment
from utilities import create_channel
from utilities import create_pulse_generator
from utilities import compute_comp_area
from utilities import set_channel_conductance
from utilities import create_output_table
from utilities import plot_vm_table
from collections import namedtuple
from channels_2 import channel_settings
from copy import copy
EREST_ACT = -70e-3 #: Resting membrane potential

channel_setting = [Na_chan, k_chan]

VMIN = -30e-3 + EREST_ACT
VMAX = 120e-3 + EREST_ACT
VDIVS = 3000
CAMIN = 0
CAMIX = 1
CADIVS = 3000

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

    # Channel information.
    sa, x_sa = compute_comp_area(diameter, length)
    na_g = 120E-3 * sa * 1E4
    na_ek = 115E-3 + EREST_ACT
    k_g = 36e-3 * sa * 1E4
    k_ek = -12E-3 + EREST_ACT

    # Stimulus information
    inj_delay = 20E-3
    inj_amp = 1E-9
    inj_width = 40E-3

    # Create cell
    chicken_model = create_swc_model(root_name='E19', file_name='E19-cell_filling-caudal.CNG.swc', RM=RM, CM=CM, RA=RA, ELEAK=Em, initVM=Em)
    soma = moose.element('/E19[0]/soma')

    # Create channels
    channels_set = create_set_of_channels(channel_settings, VDIVS, VMIN, VMAX, CADIVS, CAMIN, CAMAX)

    # Fetch all compartment paths.
    moose_paths = []
    for comp in moose.wildcardFind(chicken_model.path+'/#[TYPE=Compartment]'):
        moose_paths.append(comp.path)


    # connect pulse gen
    pulse_inject = create_pulse_generator(soma, inj_width, inj_amp, delay=inj_delay)

    # Output table
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    soma_i_table = create_output_table(table_element='/output', table_name='somaIm')

    # Connect output tables
    moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    moose.connect(soma_i_table, 'requestOut', pulse_inject, 'getOutputValue')

    # Set moose simulation clocks
    for lable in range(7):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # Plot output tables.
    v_plot = plot_vm_table(simtime,"soma voltage", soma_v_table, soma_i_table)
    plt.grid(True)
    plt.legend(['v', 'i'])
    plt.show()

main()
