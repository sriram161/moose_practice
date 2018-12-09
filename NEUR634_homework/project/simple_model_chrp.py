# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#bash-4.2$ module add python/2.7.15
#bash-4.2$ module add moose

import moose
import numpy as np
import matplotlib.pyplot as plt
from utilities_p import create_comp_model
from utilities_p import create_pulse_generator
from utilities_p import create_output_table
from utilities_p import plot_vm_table
from utilities_p import create_set_of_channels
from channels_p_2 import channel_settings
from channels_p_2 import ca_params
from utilities_p import create_compartment
from utilities_p import compute_comp_area
from utilities_p import create_ca_conc_pool
from utilities_p import copy_ca_pools_moose_paths
from utilities_p import connect_ca_pool_to_chan
from utilities_p import copy_connect_channel_moose_paths

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
    func_1.expr = '{A}*cos(2*pi*(({f1}-{f0})/{T})*x^2 + 2*pi*{f1}*x + {p})+{o}'.format(f0=f0, f1=f1, T=T, A=amp, p=phase, o=amp_offset)
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
        inj_amp = 10E-9
        inj_width = 40E-3

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
    plotdt = 0.25e-3

    diameter = 20e-6
    length = 20e-6

    inj_delay = 20E-3
    inj_amp = 2E-3 # Pleace chirp amplitudes 2.5E-3 and 15E-3
    inj_width = 1

    # Model creation
    soma, moose_paths = simple_model(model_name, comp_passive, channel_settings, ca_params, length, diameter)
    chirp_test = chirp(gen_name="chirp",amp=inj_amp, f0=0.1, f1=40, T=1, start=inj_delay, end=inj_width+inj_delay, simdt=simdt,amp_offset=0)
    moose.connect(chirp_test, 'valueOut', soma, 'injectMsg')
    # Output table
    tabs = creat_moose_tables()
    soma_c_table = create_output_table(table_element='/output', table_name='somchirpIm')
    moose.connect(soma_c_table, 'requestOut', chirp_test, 'getValue')

    # Set moose simulation clocks
    for lable in range(7):
        moose.setClock(lable, simdt)
    moose.setClock(8, plotdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    # set conductance for a list to Ca_v1, Ca_V2 and CC
    from collections import namedtuple
    cond = namedtuple('cond', 'k Ltype Ntype cl')
    test_conductances = [cond(k=0.3775621, Ltype=0.18, Ntype=0.4, cl=40),]

    for K, V1, V2, cc in test_conductances:
        moose.element('/soma/K').Gbar = K #* compute_comp_area(length, diameter)[0] *1E4
        moose.element('/soma/Ca_V1').Gbar = V1 #* compute_comp_area(length, diameter)[0] *1E4
        moose.element('/soma/Ca_V2').Gbar = V2 #* compute_comp_area(length, diameter)[0] *1E4
        moose.element('/soma/ca_cc').Gbar = cc #* compute_comp_area(length, diameter)[0] *1E4
        moose.reinit()
        moose.start(simtime)
        #plot_internal_currents(*tabs['internal_currents'])
        plot_vm_table(simtime, tabs['vm'][0], title='Conductances: ca_V1(L): {1}, Ca_V2 (N) :{0}, ca_cc :{2} K : {3}'.format(V1, V2, cc, K), xlab="Time in Seconds", ylab="Volage (V)")
        plt.show()

    # plot chirp signal
    t = np.arange(0, simtime, 1/len(soma_c_table.vector))
    plt.plot(t, soma_c_table.vector)
    plt.xlabel("time in seconds")
    plt.ylabel("voltage (V)")
    plt.show()

    current_time_domain = soma_c_table.vector
    voltage_time_domain = tabs['vm'][0].vector
    import scipy.fftpack as fftpack
    current_fft = fftpack.fft(current_time_domain)
    voltage_fft = fftpack.fft(voltage_time_domain)
    current_magnitude = np.abs(current_fft)
    voltage_magnitude = np.abs(voltage_fft)
    current_phase = np.angle(current_fft)
    voltage_phase = np.angle(voltage_fft)
    freq_current = np.fft.fftfreq(len(current_fft), 1/len(soma_c_table.vector))
    freq_voltage = np.fft.fftfreq(len(voltage_fft), 1/len(soma_c_table.vector))
    N = len(current_fft)
    plt.figure("soma_current")
    plt.plot(freq_current, current_magnitude)
    plt.xlabel('Frequecy (Hz)')
    plt.ylabel('Magnitude (mA)')
    plt.show()

    plt.figure("membrane voltage")
    plt.plot(freq_voltage, voltage_magnitude)
    plt.xlabel('Frequecy (Hz)')
    plt.ylabel('Volts (V)')
    plt.show()

    plt.figure("membrane voltage")
    plt.plot(freq_voltage, voltage_magnitude/current_magnitude)
    plt.xlabel('Frequecy (Hz)')
    plt.ylabel('ohms ($\Omega$)')
    plt.show()

    plt.title('membrance impedance')
    plt.plot(freq_voltage, voltage_phase - current_phase)
    plt.xlabel('Frequecy (Hz)')
    plt.ylabel('phase ($\Theta$)')
    plt.show()

if __name__ == "__main__":
    model_name = 'soma'
    channel_settings = channel_settings
    comp_passive = {'RM':1/(0.06), 'CM': 1,'RA':4, 'EM': -50e-3}
    main(model_name, comp_passive, channel_settings, ca_params=ca_params)
