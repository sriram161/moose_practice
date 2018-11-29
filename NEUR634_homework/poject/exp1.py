# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#bash-4.2$ module add python/2.7.15
#bash-4.2$ module add moose

import moose
import numpy as np
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

def chirp(gen_name="chirp", f0=1, f1=50, T=0.8, start=0.1, end=0.5, simdt=10E-5):
    func_1 = moose.Func("/"+gen_name)
    func_1.mode = 3
    func_1.expr = 'cos(2*pi*({f1}-{f0})/{T}*x^2 + 2*pi*{f1}*x)'.format(f0=f0, f1=f1, T=T)
    input = moose.StimulusTable('/xtab')
    xarr = np.arange(start, end, simdt)
    input.vector = xarr
    input.startTime = 0.0
    input.stepPosition = xarr[0]
    input.stopTime = xarr[-1] - xarr[0]
    moose.connect(input, 'output', func_1, 'xIn')
    return func_1


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
    simtime = 50E-3
    simdt = 0.25e-5
    plotdt = 0.25e-3

    # Model creation
    cell, cell_comp_paths = cell_prototype(model_name, file_name, comp_passive, channel_settings, ca_params)
    soma = moose.element(cell.path +'/soma')

    pulse_inject_50pA = create_pulse_generator('pulse2', soma, 50E-3, 50E-12, delay=10E-3)
    chirp_test = chirp(gen_name="chirp", f0=1, f1=50, T=0.8, start=10E-3, end=20E-3, simdt=simdt)
    tab = moose.Table('/check')
    moose.connect(tab, 'requestOut', chirp_test, 'getValue')
    moose.connect(chirp_test, 'valueOut', soma, 'injectMsg')

    # Output table
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    soma_i_table = create_output_table(table_element='/output', table_name='somaIm3')

    # Connect output tables     #source message [data into the component]  desination message(out of the compartments)
    moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    moose.connect(soma_i_table, 'requestOut', pulse_inject_50pA, 'getOutputValue')

    # Set moose simulation clocks
    for lable in range(7):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # Plot output tables.
    v_plot = plot_vm_table(simtime,soma_v_table, soma_i_table, title="soma vs i")
    plt.grid(True)
    plt.legend(['v', 'i'])
    plt.show()

if __name__ == "__main__":
    model_name = 'lts'
    file_name = 'interneuron.swc'
    channel_settings = channel_settings
    comp_passive = {'RM':20, 'CM': 1e-6 * 1E4,'RA':4, 'EM': -50e-3} # check with Dan????
    main(model_name, file_name, comp_passive, channel_settings)
