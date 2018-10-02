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
from copy import copy
EREST_ACT = -70e-3 #: Resting membrane potential

AlphaBetaparams = namedtuple('AlphaBetaparams', 'A_A A_B A_C A_D A_F B_A B_B B_C B_D B_F')
Na_m_params = AlphaBetaparams(
              A_A=1e5 * (25e-3 + EREST_ACT), A_B=-1e5, A_C=-1.0, A_D=-25e-3 - EREST_ACT, A_F=-10e-3,
              B_A=4e3, B_B=0.0, B_C=0.0, B_D=0.0 - EREST_ACT, B_F=18e-3)

Na_h_params = AlphaBetaparams(
              A_A=70.0, A_B=0.0, A_C=0.0, A_D=0.0 - EREST_ACT, A_F=0.02,
              B_A=1000.0, B_B=0.0, B_C=1.0, B_D=-30E-3 - EREST_ACT, B_F=-0.01)

K_n_params = AlphaBetaparams(
              A_A=1e4 * (10e-3 + EREST_ACT), A_B=-1e4, A_C=-1.0, A_D=-10e-3 - EREST_ACT, A_F=-10e-3,
              B_A=0.125e3, B_B=0.0, B_C=0.0, B_D=0.0 - EREST_ACT, B_F=80e-3)

channel_param_template = {'chan_name':None, 'x_params': None, 'y_params': None, 'x_pow': None, 'y_pow': None,
                          'g_max': None, 'ek': None}

Na_chan = copy(channel_param_template)
k_chan = copy(channel_param_template)

Na_chan['chan_name']='Na'
Na_chan['x_params']= Na_m_params
Na_chan['y_params']= Na_h_params
Na_chan['x_pow']= 3
Na_chan['y_pow']= 1
Na_chan['g_max']= 120E-3
Na_chan['e_k']= 115E-3 + EREST_ACT

k_chan['chan_name']= 'K'
k_chan['x_params']= Na_m_params
k_chan['x_pow']= 4
k_chan['g_max']= 36e-3
k_chan['e_k']= -12E-3 + EREST_ACT

channel_setting = [Na_chan, k_chan]

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
    soma = create_compartment('soma', length, diameter, RM, CM, initVM=EREST_ACT, ELEAK=Em)

    # Create channels
    k_chan = create_channel(chan_name='K',vdivs=VDIVS, vmin=VMIN, vmax=VMAX,
                        x_params=K_n_params, xpow=4)
    Na_chan = create_channel(chan_name='Na',vdivs=VDIVS, vmin=VMIN, vmax=VMAX,
                        x_params=Na_m_params, xpow=3, y_params=Na_h_params, ypow=1)

    # Set conductances
    nachan = moose.copy(Na_chan, soma.path, 'Na', 1)
    kchan = moose.copy(K_chan, soma.path, 'K', 1)

    nachan = set_channel_conductance(nachan, na_g, na_ek)
    kchan = set_channel_conductance(kchan, k_g, k_ek)

    # Add channels to soma
    moose.connect(nachan, 'channel', soma, 'channel', 'OneToOne')
    moose.connect(kchan, 'channel', soma, 'channel', 'OneToOne')

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
