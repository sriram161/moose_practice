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
from utilities import create_output_table
from utilities import plot_vm_table
from utilities import create_set_of_channels
from utilities import copy_connect_channel_moose_paths
from utilities import create_ca_conc_pool
from utilities import copy_ca_pools_moose_paths
from utilities import connect_ca_pool_to_chan
from utilities import create_swc_model
from channels_1 import channel_settings
from channels_1 import ca_params

EREST_ACT = -70e-3 #: Resting membrane potential
VMIN = -30e-3 + EREST_ACT
VMAX = 120e-3 + EREST_ACT
VDIVS = 3000
CAMIN = 0
CAMAX = 1
CADIVS = 10E3

def main(experiment_title, ca_g_max, skca_g_max):
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
    RA = 4

    # Stimulus information
    inj_delay = 20E-3
    inj_amp = 1E-9
    inj_width = 40E-3

    channel_settings['CaL']['g_max'] = ca_g_max
    channel_settings['SKca']['g_max'] = skca_g_max

    # Create cell
    chicken_model = create_swc_model(root_name='E19', file_name='E19-cell_filling-caudal.CNG.swc', RM=RM, CM=CM, RA=RA, ELEAK=Em, initVM=Em)
    soma = moose.element('/E19[0]/soma')

    # Create channels
    channels_set = create_set_of_channels(channel_settings, VDIVS,  VMIN, VMAX, CADIVS, CAMIN, CAMAX)

    moose_paths = [soma.path]
    for channel_name, channel_obj in channels_set.items():
        copy_connect_channel_moose_paths(channel_obj, channel_name, moose_paths)

    # Create calcium pools in library.
    ca_pool = create_ca_conc_pool(ca_params)

    # copy calcium pools to all compartments.
    copy_ca_pools_moose_paths(ca_pool, 'CaPool', moose_paths)

    # Connect calciums pools to channels in compartments.
    connect_ca_pool_to_chan(chan_name='SKca', chan_type='ca_dependent', calname='CaPool', moose_paths=moose_paths)
    connect_ca_pool_to_chan(chan_name='CaL', chan_type='ca_permeable', calname='CaPool', moose_paths=moose_paths)

    # connect pulse gen.
    pulse_inject = create_pulse_generator(soma, inj_width, inj_amp, delay=inj_delay)

    # Output table.
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    soma_i_table = create_output_table(table_element='/output', table_name='somaIm')

    # Connect output tables.
    moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    moose.connect(soma_i_table, 'requestOut', pulse_inject, 'getOutputValue')

    # Set moose simulation clocks.
    for lable in range(10):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # Plot output tables.
    v_plot = plot_vm_table(simtime, soma_v_table, soma_i_table, title=experiment_title.format(ca_g_max, skca_g_max), xlab='Time', ylab='voltage')
    plt.grid(True)
    plt.legend(['v', 'i'])
    plt.show()

main(experiment_title="Soma voltage when calcium g_max= {} SKca g_max = {}", ca_g_max=0, skca_g_max=0)
