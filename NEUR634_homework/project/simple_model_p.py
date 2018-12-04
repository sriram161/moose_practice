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
from utilities_p import create_ca_conc_pool
from utilities_p import copy_ca_pools_moose_paths
from utilities_p import connect_ca_pool_to_chan
from channels_p import channel_settings
from channels_p import ca_params
from utilities import create_compartment
from utilities import compute_comp_area

VMIN = -90e-3
VMAX = 120e-3
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

def simple_model(model_name, comp_passive, channel_settings, ca_params, length, diameter):
        # Simulation information.
        simtime = 500E-3
        simdt = 0.25e-5
        plotdt = 0.25e-3

        diameter = diameter
        length = length

        inj_delay = 20E-3
        inj_amp = 1E-9
        inj_width = 100E-3

        # Model creation
        soma = create_compartment('soma', length, diameter, comp_passive['RM'], comp_passive['CM'], initVM=comp_passive['EM'], ELEAK=comp_passive['EM'])
        moose_paths = [soma.path]
        channels_set = create_set_of_channels('soma', channel_settings, VDIVS,  VMIN, VMAX, CADIVS, CAMIN, CAMAX)
        for channel_name, channel_obj in channels_set.items():
            copy_connect_channel_moose_paths(channel_obj, channel_name, moose_paths)

        if ca_params:
            ca_pool = create_ca_conc_pool('soma', ca_params)
            copy_ca_pools_moose_paths(ca_pool, 'CaPool', moose_paths, ca_params.bufCapacity)
        for channel_name, channel_obj in channel_settings.items():
            if channel_obj.get('chan_type'):
               connect_ca_pool_to_chan(channel_name, channel_obj['chan_type'], 'CaPool', moose_paths)
        return soma, moose_paths

def plot_internal_currents(soma_i_table, soma_i_table1, soma_i_table2, soma_i_table3, soma_i_table4):
    plt.figure("internal currents")
    #plot_vm_table(simtime,soma_i_table, soma_i_table1, soma_i_table2, soma_i_table3, title="soma vs i")
    plt.plot(soma_i_table.vector, label='Ca_v2')
    plt.plot(soma_i_table1.vector ,label='Ca_V1')
    plt.plot(soma_i_table2.vector ,label='K')
    plt.plot(soma_i_table3.vector ,label='ca_cc')
    plt.legend()

    plt.figure("capool")
    plt.plot(soma_i_table4.vector ,label='pool')
    plt.legend()

def creat_moose_tables():
    soma_v_table = create_output_table(table_element='/output', table_name='somaVm')
    soma_i_table = create_output_table(table_element='/output', table_name='somIm')
    soma_i_table1 = create_output_table(table_element='/output', table_name='somIm1')
    soma_i_table2 = create_output_table(table_element='/output', table_name='somIm2')
    soma_i_table3 = create_output_table(table_element='/output', table_name='somIm3')
    soma_i_table4 = create_output_table(table_element='/output', table_name='somIm4')

    moose.connect(soma_v_table, 'requestOut', moose.element('/soma'), 'getVm')
    moose.connect(soma_i_table, 'requestOut', moose.element('/soma/Ca_V2'), 'getIk')
    moose.connect(soma_i_table1, 'requestOut', moose.element('/soma/Ca_V1'), 'getIk')
    moose.connect(soma_i_table2, 'requestOut', moose.element('/soma/K'), 'getIk')
    moose.connect(soma_i_table3, 'requestOut', moose.element('/soma/ca_cc'), 'getIk')
    moose.connect(soma_i_table4, 'requestOut', moose.element('/soma/CaPool'), 'getCa')
    return {'vm': [soma_v_table], 'internal_currents': [soma_i_table, soma_i_table1, soma_i_table2, soma_i_table3, soma_i_table4]}

def main(model_name, comp_passive, channel_settings, ca_params):
    # Simulation information.
    simtime = 1
    simdt = 0.25e-5
    #simdt = 0.1e-6
    plotdt = 0.25e-3

    diameter = 20e-6
    length = 20e-6


    # Model creation
    soma, moose_paths = simple_model(model_name, comp_passive, channel_settings, ca_params, length, diameter)
    # chirp_test = chirp(gen_name="chirp",amp=1E-9, f0=0.1, f1=500, T=0.8, start=inj_delay, end=inj_width+inj_delay, simdt=simdt,amp_offset=5E-9)

    # moose.connect(chirp_test, 'valueOut', soma, 'injectMsg')
    # Output table
    tabs = creat_moose_tables()
    # moose.connect(soma_i_table, 'requestOut', chirp_test, 'getValue')

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
    from collections import namedtuple
    cond = namedtuple('cond', 'k Ltype Ntype cl')
    # Final execution test
    # test_conductances = [cond(k=0.5E-3, Ltype=0.18E-3, Ntype=0.4E-3, cl=40E-3),  # control test
    #                  cond(k=0.5E-3, Ltype=0.18E-3, Ntype=0, cl=40E-3),  # L-type frequecy reduce test
    #                  cond(k=0.5E-3, Ltype=0, Ntype=0.4E-3, cl=40E-3),  # N-type amplitude reduce test
    #                  cond(k=0.5E-3, Ltype=0.18E-3, Ntype=0.4E-3, cl=0),   # cl-type Current abolish test
    #                  cond(k=0, Ltype=0.18E-3, Ntype=0.4E-3, cl=40E-3)    # K AHP reduce test
    #                  ]
    # Set to -15mv when cl current is blocked.
    # test_conductances = [
    #                  cond(k=0.5E-3*1E15, Ltype=0.18E-3, Ntype=0.4E-3, cl=0),   # cl-type Current abolish test
    #                  ]
    # Set to -15mv when cl current is blocked.
    test_conductances = [
                #     cond(k=0.5E-3 * 0.5, Ltype=0.18E-6 * 10, Ntype=0.4E-5 * 11, cl=0),   # cl-type Current abolish test
                     #cond(k=0.5E-3 , Ltype=0, Ntype=0.4E-5, cl=100E-3),   # cl-type Current abolish test
                     # cond(k=0.5E-3, Ltype=0.18E-3, Ntype=0.4E-3, cl=40E-3),   # cl-type Current abolish test
                     # cond(k=0.5, Ltype=0.18, Ntype=0.4, cl=40),   # cl-type Current abolish test
                    # cond(k=0.5, Ltype=0.18, Ntype=0.4, cl=0),   # cl-type Current abolish test
                     cond(k=0.3775621, Ltype=0.18, Ntype=0.4, cl=40),   # cl-type Current abolish test
                     ]


    for K, V1, V2, cc in test_conductances:
        moose.element('/soma/K').Gbar = K #* compute_comp_area(length, diameter)[0] * 1E4
        moose.element('/soma/Ca_V1').Gbar = V1 #* compute_comp_area(length, diameter)[0] * 1E4
        moose.element('/soma/Ca_V2').Gbar = V2 #* compute_comp_area(length, diameter)[0] * 1E4
        moose.element('/soma/ca_cc').Gbar = cc #* compute_comp_area(length, diameter)[0] * 1E4
        moose.reinit()
        moose.start(simtime)
        #plot_internal_currents(*tabs['internal_currents'])
        plot_vm_table(simtime, tabs['vm'][0], title='Conductances: ca_V1(L): {0}, Ca_V2 (N) :{1}, ca_cc :{2} K : {3}'.format(V1, V2, cc, K), xlab="Time in Seconds", ylab="Volage (V)")
        plt.show()

    # from moose_nerp.graph import plot_channel
    # for channel in channel_settings:
    #     libchan=moose.element('/library/soma/'+channel)
    #     plot_channel.plot_gate_params(libchan,1,VMIN, VMAX, CAMIN, CAMAX)
    # plt.show()

if __name__ == "__main__":
    model_name = 'soma'
    channel_settings = channel_settings
    comp_passive = {'RM':1/(0.06), 'CM': 1,'RA':4, 'EM': -50e-3} # check with Dan????
    main(model_name, comp_passive, channel_settings, ca_params=ca_params)
