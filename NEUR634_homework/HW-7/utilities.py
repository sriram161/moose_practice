# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import moose
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from itertools import chain
from collections import namedtuple
import scipy.constants.physical_constants as constants
FARADAY_CONST = constants.get("Faraday constant")[0]
# TODO copy calcium pool to compartment.
# TODO connect calcium pool to calcium dependent channel.

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

def create_channel(chan_name, vdivs, vmin, vmax, cadivs, camin, camax,
                   x_params, xpow, tick=-1, y_params=None, ypow=0, zpow=0, z_params=None):
    if not moose.exists('/library'):
        moose.Neutral('/library')
    chan_comp = moose.HHChannel('/library/' + chan_name)
    chan_comp.tick = tick
    if xpow: # GateX
        chan_comp.Xpower = xpow
        params = x_params + (vdivs, vmin, vmax)
        moose.element(chan_comp.path + '/gateX').setupAlpha(list(params))
    if ypow: # GateY
        chan_comp.Ypower = ypow
        params = y_params + (vdivs, vmin, vmax)
        moose.element(chan_comp.path + '/gateY').setupAlpha(list(params))
    if zpow: # GateZ
        chan_comp.Zpower = zpow
        create_conc_dependent_z_gate(chan_comp, z_params, cadivs, camin, camax)
    return chan_comp

def create_conc_dependent_z_gate(chan, params, cadivs, camin, camax):
    zgate = moose.HHGate(chan.path + '/gateZ')
    zgate.min, zgate.max = camin, camax
    ca_conc_points = np.linspace(camin, camax, cadivs)
    caterm = (ca_conc_points/params.kd)
    caterm = caterm* params.power
    z_inf = caterm/(1+caterm)
    z_tau = params.tau*np.ones(len(ca_array))
    zgate.tableA = z_inf / z_tau
    zgate.tableB = 1 / z_tau
    chan.useConcentration = True
    return chan

def create_ca_conc_pool(params):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    ca_pool = moose.CaConc(lib.path+'/'+params.caName)
    ca_pool.CaBasal = params.caBasal
    ca_pool.ceiling = 1
    ca_pool.floor = 0
    ca_pool.thick = params.caThick
    ca_pool.tau = params.caTau
    return ca_pool

def set_channel_conductance(chan, gbar, E_nerst):
    chan.Gbar = gbar
    chan.Ek = E_nerst
    return chan

def create_set_of_channels(channel_settings, vdivs, vmin, vmax, cadivs, camin, camax):
    chan_set = {}
    for settings in channel_settings:
        chan = create_channel(chan_name=settings.get('chan_name'),
                              vdivs=vdivs, vmin=vmin, vmax=vmax,
                              cadivs=cadivs, camin=camin, camax=camax,
                              x_params=settings.get('x_params'), xpow=settings.get('x_pow'),
                              y_params=settings.get('y_params'), ypow=settings.get('y_pow'),
                              z_params=settings.get('z_params'), zpow=settings.get('z_pow'))
        set_channel_conductance(chan, gbar=settings.get('g_max'), E_nerst=settings.get('e_k'))
    return chan_set

def copy_connect_channel_moose_paths(moose_chan, chan_name, moose_paths):
    for moose_path in moose_paths:
        _chan = moose.copy(moose_chan, moose_path, chan_name, 1)
        moose.connect(_chan, 'channel', moose.element(moose_path), 'channel', 'OneToOne')

def copy_connect_ca_pools_moose_paths(ca_pool, pool_name, buf_capacity, moose_paths):
    global FARADAY_CONST
    for moose_path in moose_paths:
        comp = moose.element(moose_path)
        _pool = moose.copy(ca_pool, comp, pool_name, 1)
        _pool.length = comp.length
        _pool.diameter = comp.diameter
        curved_sa = compute_comp_area(comp.diameter, comp.length)[0]
        volume = curved_sa * _pool.thick
        _pool.B = 1/(FARADAY_CONST * volume * 2) / buf_capacity

def connect_ca_pool_to_chan(settings, moose_paths):
    for moose_path in moose_paths:
        comp = moose.element(moose_path)
        _pool = moose.element(comp.path + '/' + )
    # TODO connect calcium pool to channels.


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
