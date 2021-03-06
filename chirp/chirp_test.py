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
from channels_1 import channel_settings
from utilities import create_compartment

EREST_ACT = -70e-3 #: Resting membrane potential ??? where in paper???
VMIN = -30e-3 + EREST_ACT
VMAX = 120e-3 + EREST_ACT
VDIVS = 3000
CAMAX = 1
CAMIN = 0
CADIVS = 10E3

def chirp(gen_name="chirp", amp=1, f0=1, f1=50, T=0.8, start=0.1, end=0.5, simdt=10E-5, phase=0, amp_offset=0):
    chirper = moose.element('/chirpgen') if moose.exists('/chirpgen') else moose.Neutral('/chirpgen')
    func_1 = moose.Func(chirper.path+'/'+gen_name)
    func_1.mode = 3
    func_1.expr = '{A}*cos(2*pi*({f1}-{f0})/{T}*x^2 + 2*pi*{f1}*x + {p})+{o}'.format(f0=f0, f1=f1, T=T, A=amp, p=phase, o=amp_offset)
    input = moose.StimulusTable(chirper.path+'/xtab')
    xarr = np.arange(start, end, simdt)
    input.vector = xarr
    input.startTime = 0.0
    input.stepPosition = xarr[0]
    input.stopTime = xarr[-1] - xarr[0]
    moose.connect(input, 'output', func_1, 'xIn')
    moose.useClock(0, '%s/##[TYPE=StimulusTable]' % (chirper.path), 'process')
    moose.useClock(0,'%s/##[TYPE=Func]' % (chirper.path), 'process')
    return func_1

def main(model_name, file_name, comp_passive, channel_settings):
    # Simulation information.
    simtime = 100E-3
    simdt = 0.25e-5
    plotdt = 0.25e-3

    diameter = 30e-6
    length = 50e-6
    Em = EREST_ACT + 10.613e-3
    CM = 1e-6 * 1e4
    RM = 1 /(0.3E-3 * 1e4)

    inj_delay = 20E-3
    inj_amp = 1E-9
    inj_width = 40E-3

    # Model creation
    soma = create_compartment('soma', length, diameter, RM, CM, initVM=EREST_ACT, ELEAK=Em)
    moose_paths = [soma.path]
    channels_set = create_set_of_channels('soma', channel_settings, VDIVS,  VMIN, VMAX, CADIVS, CAMIN, CAMAX)
    for channel_name, channel_obj in channels_set.items():
        copy_connect_channel_moose_paths(channel_obj, channel_name, moose_paths)

    chirp_test = chirp(gen_name="chirp",amp=1E-9, f0=0.1, f1=500, T=0.8, start=inj_delay, end=inj_width+inj_delay, simdt=simdt,amp_offset=5E-9)
    moose.reinit()
    moose.connect(chirp_test, 'valueOut', soma, 'injectMsg')

    #pulse_inject = create_pulse_generator('pulse', soma, inj_width, inj_amp, delay=inj_delay)

    # Output table
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    soma_i_table = create_output_table(table_element='/output', table_name='somaIm3')

    # moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    # moose.connect(soma_i_table, 'requestOut', pulse_inject, 'getOutputValue')
    # Connect output tables     #source message [data into the component]  desination message(out of the compartments)
    moose.connect(soma_v_table, 'requestOut', soma, 'getVm')
    moose.connect(soma_i_table, 'requestOut', chirp_test, 'getValue')

    # Set moose simulation clocks
    for lable in range(7):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # Plot output tables.
    #v_plot = plot_vm_table(simtime,soma_v_table, soma_i_table, title="soma vs i")
    #plt.grid(True)
    #plt.legend(['v', 'i'])
    #plt.show()

    import matplotlib.pyplot as plt
    plt.subplot(211)
    plt.plot(soma_i_table.vector)
    plt.subplot(212)
    plt.plot(soma_v_table.vector)
    plt.show()

if __name__ == "__main__":
    model_name = 'lts'
    file_name = 'interneuron.swc'
    channel_settings = channel_settings
    comp_passive = {'RM':20, 'CM': 1e-6 * 1E4,'RA':4, 'EM': -50e-3} # check with Dan????
    main(model_name, file_name, comp_passive, channel_settings)
