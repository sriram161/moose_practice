# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#bash-4.2$ module add python/2.7.15
#bash-4.2$ module add moose

import moose
import matplotlib.pyplot as plt
from utilities import create_comp_model
from utilities import create_pulse_generator
from utilities import create_output_table
from utilities import plot_vm_table
from utilities import create_set_of_channels
from utilities import copy_connect_channel_moose_paths
from utilities import create_ca_conc_pool
from utilities import copy_ca_pools_moose_paths
from utilities import connect_ca_pool_to_chan
from channels import channel_settings
from channels import ca_params

EREST_ACT = -50e-3 #: Resting membrane potential ??? where in paper???
VMIN = -30e-3 + EREST_ACT
VMAX = 120e-3 + EREST_ACT
VDIVS = 3000
CAMAX = 1
CAMIN = 0
CADIVS = 10E3

def cell_prototype(model_name, file_name, comp_passive, channel_settings, caparams=None):
    model = create_comp_model(model_name, file_name, comp_RM=comp_passive['RM'],
                              comp_CM=comp_passive['CM'], comp_RA=comp_passive['RA'],
                              comp_ELEAK=comp_passive['EM'], comp_initVm=comp_passive['EM'])
    soma = moose.element(model.path +'/soma')

    # Create channels
    channels_set = create_set_of_channels(model_name, channel_settings, VDIVS,  VMIN, VMAX, CADIVS, CAMIN, CAMAX)

    # Fetch all compartment paths.
    moose_paths = []
    for comp in moose.wildcardFind(model.path+'/#[TYPE=Compartment]'):
        moose_paths.append(comp.path)

    # Copy all channels to compartments.
    for channel_name, channel_obj in channels_set.items():
            copy_connect_channel_moose_paths(channel_obj, channel_name, moose_paths)

    # Create calcium buffer pools
    if caparams:
        ca_pool = create_ca_conc_pool(model_name, ca_params)
        copy_ca_pools_moose_paths(ca_pool, 'CaPool', moose_paths)
    for channel_name, channel_obj in channel_settings.items():
        if channel_obj.get('chan_type'):
           connect_ca_pool_to_chan(channel_name, channel_obj['chan_type'], 'CaPool', moose_paths)
    return (model, moose_paths)

def main(model_name, file_name, comp_passive, channel_settings):
    # Simulation information.
    simtime = 11
    simdt = 0.25e-5
    plotdt = 0.25e-3

    # Stimulus information
    inj_delay = 20E-3
    inj_amp = 1E-9
    inj_width = 40E-3

    # Model creation
    # cell, cell_comp_paths = cell_prototype(model_name, file_name, comp_passive, channel_settings, ca_params)
    # soma = moose.element(cell.path +'/soma')
    from utilities import create_compartment
    soma = create_compartment('soma', 1, 1, 1, 1, initVM=1, ELEAK=1)

    # connect pulse gen
    pulse_inject_n50pA = create_pulse_generator('pulse1', soma, 50E-3, -50E-12, delay=10E-3)
    pulse_inject_50pA = create_pulse_generator('pulse2', soma, 50E-3, 50E-12, delay=10E-3)
    import moose
    pulse3 = moose.PulseGen('pulse3')
    pulse3.setCount(3)
    pulse3.delay[0] = 10E-3
    pulse3.level[0] = -20E-12
    pulse3.width[0] =  2.5 # 50E-3
    pulse3.delay[1] = pulse3.width[0]
    pulse3.level[1] = -10E-12
    pulse3.width[1] =  2.5 #50E-3  # from figure. 1 C
    pulse3.delay[2] = 1E9


    # Output table
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    #soma_i_table1 = create_output_table(table_element='/output', table_name='somaIm1')
    #soma_i_table2 = create_output_table(table_element='/output', table_name='somaIm2')
    soma_i_table3 = create_output_table(table_element='/output', table_name='somaIm3')

    # Connect output tables     #source message [data into the component]  desination message(out of the compartments)
    #moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    #moose.connect(soma_i_table1, 'requestOut', pulse_inject_50pA, 'getOutputValue')
    #moose.connect(soma_i_table2, 'requestOut', pulse_inject_n50pA, 'getOutputValue')
    moose.connect(soma_i_table3, 'requestOut', pulse3, 'getOutputValue')

    # Set moose simulation clocks
    for lable in range(7):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # Plot output tables.
    v_plot = plot_vm_table(simtime,soma_i_table3, title="soma")
    plt.grid(True)
    # plt.legend()
    plt.show()


if __name__ == "__main__":
    model_name = 'lts'
    file_name = 'interneuron.swc'
    channel_settings = channel_settings
    comp_passive = {'RM':20, 'CM': 1e-6 * 1E4,'RA':4, 'EM': -50e-3} # check with Dan????
    main(model_name, file_name, comp_passive, channel_settings)
