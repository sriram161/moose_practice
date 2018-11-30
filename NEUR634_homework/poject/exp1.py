# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#bash-4.2$ module add python/2.7.15
#bash-4.2$ module add moose

import moose
import sys
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

VMIN = -100e-3
VMAX = 50E-3
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

def main(model_name, file_name, comp_passive, channel_settings, simtime = 100E-3, simdt = 0.25e-5):
    # Simulation information.
    simtime = simtime
    simdt = simdt
    plotdt = 0.25e-3

    # Model creation
    cell, cell_comp_paths = cell_prototype(model_name, file_name, comp_passive, channel_settings, ca_params)
    soma = moose.element(cell.path +'/soma')

    pulse_inject_50pA = create_pulse_generator('pulse2', soma, 50E-3, 0, delay=10E-3) #50E-12

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
    return soma_v_table, soma_i_table


if __name__ == "__main__":
    model_name = 'lts'
    file_name = sys.argv[1]
    ca_v1_flag = int(sys.argv[2])
    ca_v2_flag = int(sys.argv[3])
    ca_cc_flag = int(sys.argv[4])
    simtime = 100E-3
    simdt = 0.25e-5

    channel_settings = channel_settings
    if ca_v1_flag:
        channel_settings['Ca_V1']['g_max'] = 0
    if ca_v2_flag:
        channel_settings['Ca_V2']['g_max'] = 0
    if ca_cc_flag:
        channel_settings['ca_cc']['g_max'] = 0

    comp_passive = {'RM':1/(0.06E-3 * 1E4), 'CM': 1e-6 * 1E4,'RA':4, 'EM': -30e-3} # check with Dan????
    soma_v, soma_i = main(model_name, file_name, comp_passive, channel_settings, simtime)

    # Plot output tables.
    v_plot = plot_vm_table(simtime,soma_v, soma_i, title="soma time domain", xlab="Time (Seconds)", ylab= "Voltage (V)")
    v_plot.legend(['v', 'i'])

    plt.show()
    # frequency domain plot.
    fft = np.fft.fft(soma_v.vector)
    freq = np.fft.fftfreq(len(fft), simdt)
    plt.figure("soma frequency domain")
    plt.plot(freq, np.abs(fft))
    plt.xlabel("Frequency (Hz)")
    plt.ylabel(" Abs(Amplitude) Volts")
    #

    #######
    '''
    fft = np.fft.fft(voltage_soma_membrane_array)
    freq = np.fft.fftfreq(len(fft), simdt)
    plt.plot(freq, np.abs(fft))
    '''

    # python3 exp1.py simpleinterneuron.swc 0 0 0
