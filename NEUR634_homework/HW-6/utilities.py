# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import moose
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from itertools import chain
from collections import namedtuple

# Place creation of compartment into function.
def create_compartment(comp_name, comp_length, comp_diameter, RM, CM, RA=1.0, initVM=-65E-3, ELEAK=-65E-3):
    ''' Create a compartment
        Input: comp_name -> str
               comp_length -> float
               comp_diameter -> float
    '''
    comp = moose.Compartment('/'+ comp_name)
    comp.diameter = comp_diameter
    comp.length = comp_length
    return set_comp_values(comp, RM, CM, RA, initVM, ELEAK)
# Test:  soma = create_compartment('soma', 50E-6, 25E-6, 0.03, 2.8E3, 4.0)

def create_pulse_generator(comp_to_connect, duration, amplitude, delay=50E-3, delay_1=1E9):
    ''' Create a pulse generator and connect to a moose compartment.
    '''
    pulse = moose.PulseGen('pulse')
    pulse.delay[0] = delay  # First delay.
    pulse.width[0] = duration  # Pulse width.
    pulse.level[0] = amplitude  # Pulse amplitude.
    pulse.delay[1] = delay_1 #Don't start next pulse train.
    moose.connect(pulse, 'output', comp_to_connect, 'injectMsg')
    return pulse
# Test: pulse_1 = create_pulse_generator( soma, 100E-3, 1E-9)

def create_output_table(table_element='/output', table_name='somaVm'):
    ''' Creates and returns a moose table element.
    '''
    output = moose.Neutral(table_element)
    membrane_voltage_table = moose.Table('/'.join((table_element, table_name)))
    return membrane_voltage_table

def plot_vm_table(simtime, *comps, title="No title!!!"):
    '''' Plot traces on a common plot.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    t = np.linspace(0, simtime, len(comps[0].vector))
    arrays = [comp.vector for comp in comps]
    t_scales = [t]*len(arrays)
    plot_args = list(chain(*zip(t_scales,arrays)))
    ax.plot(*plot_args)
    ax.set_title(title)
    return ax

def create_n_dends(bunch_name, n, t_length, diameter, RM, CM, RA):
    length_per_unit = t_length / n
    bunch = OrderedDict()
    for name in [bunch_name + str(i) for i in range(n)]:
        bunch[name] = create_compartment(name, length_per_unit, diameter, RM, CM, RA)
    return bunch

def connect_n_serial(bunch):
    iterator = iter(bunch.items())
    c_name, c_item = next(iterator)
    for n_name, n_item in iterator:
        moose.connect(c_item, 'axialOut', n_item, 'handleAxial')
        c_item = n_item
    return bunch

def compute_comp_area(comp_diameter, comp_length):
    ''' Computes curved surface area and cross sectional area
    '''
    curved_surface_area = np.pi * comp_diameter * comp_length
    cross_section_area = np.pi * comp_diameter ** 2 / 4.0
    return (curved_surface_area, cross_section_area)

def set_comp_values(comp, RM, CM, RA, initVM, ELEAK):
    curved_sa, x_area = compute_comp_area(comp.diameter, comp.length)
    comp.Rm = RM / curved_sa
    comp.Cm = CM * curved_sa
    comp.Ra = RA * comp.length / x_area
    comp.initVm = initVM
    comp.Em = ELEAK
    return comp

def create_comp_model(container_name, file_name, comp_RM=None, comp_CM=None, comp_RA=None, comp_ELEAK=None, comp_initVm=None):
    'Create compartmental model from *.p file or a *.swc file.'
    if file_name.endswith('.p'):
        root_comp = moose.loadModel(file_name, cell_container_p)
    elif file_name.endswith('swc'):
        assert comp_RM is not None, "comp_RM needs valid value."
        assert comp_CM is not None, "comp_CM needs valid value."
        assert comp_RA is not None, "comp_RA needs valid value."
        assert comp_ELEAK is not None, "comp_ELEAK needs valid value."
        assert comp_initVm is not None, "comp_initVm needs valid value."
        root_comp = moose.loadModel(file_name, cell_container_p)
        for comp in moose.wildcardFind(root_comp.path+'/#[TYPE=Compartment]'):
            set_comp_values(comp, comp_RM, comp_CM, comp_RA, comp_initVm, comp_ELEAK)
    else:
        raise "Invalid cell model file type."
    return root_comp

def create_channel(chan_name, vdivs, vmin, vmax, x_params, xpow,
                   tick=-1, y_params=None, ypow=0):
    if not moose.exists('/library'):
        moose.Neutral('/library')
    chan_comp = moose.HHChannel('/library/' + chan_name)
    chan_comp.tick = tick
    if ypow:
        chan_comp.Ypower = ypow
        params = y_params + (vdivs, vmin, vmax)
        create_gate(chan_comp, list(params), gate='y')
    if xpow:
        chan_comp.Xpower = xpow
        params = x_params + (vdivs, vmin, vmax)
        create_gate(chan_comp, list(params), gate='x')
    return chan_comp

def create_gate(chan, gate_params, gate):
    print(gate_params)
    if gate.upper() == 'X':
        moose.element(chan.path + '/gateX').setupAlpha(gate_params)
    elif gate.upper() == 'Y':
        moose.element(chan.path+ '/gateY').setupAlpha(gate_params)

def set_channel_conductance(chan, gbar, E_nerst):
    chan.Gbar = gbar
    chan.Ek = E_nerst
    return chan

def create_set_of_channels(channel_settings, vdivs, vmin, vmax):
    chan_set = {}
    for settings in channel_settings:
        chan = create_channel(chan_name=settings.get('chan_name'),
                              vdivs=vdivs, vmin=vmin, vmax=vmax,
                              x_params=settings.get('x_params'), xpow=settings.get('x_pow'),
                              y_params=settings.get('y_params'), ypow=settings.get('y_pow'))
        set_channel_conductance(chan, gbar=settings.get('g_max'), E_nerst=settings.get('e_k'))
        chan_set[settings.get('chan_name')] = chan
    return chan_set

AlphaBetaparams = namedtuple('AlphaBetaparams', 'A_A A_B A_C A_D A_F B_A B_B B_C B_D B_F')
channel_param_template = {'chan_name':None, 'x_params': None, 'y_params': None, 'x_pow': None, 'y_pow': None,
                          'g_max': None, 'ek': None}

def copy_connect_channel_moose_paths(moose_chan, chan_name, moose_paths):
    for moose_path in moose_paths:
        _chan = moose.copy(moose_chan, moose_path, chan_name, 1)
        moose.connect(_chan, 'channel', moose.element(moose_path), 'channel', 'OneToOne')

def create_swc_model(root_name, file_name, RM, CM, RA, ELEAK, initVM):
 if file_name.endswith('.swc'):
     root_comp = moose.loadModel(file_name, root_name)
 else:
     raise ValueError("Please provide valid swc file as input.")

 for comp in moose.wildcardFind(root_comp.path+'/#[TYPE=Compartment]'):
     set_comp_values(comp, RM, CM, RA, initVM, ELEAK)
 return root_comp

def create_p_model(root_name, file_name):
    if file_name.endswith('.p'):
        root_comp = moose.loadModel(file_name, root_name)
        return root_comp
