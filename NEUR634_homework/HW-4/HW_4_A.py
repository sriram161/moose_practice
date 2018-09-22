import moose
import numpy as np
import wget
import matplotlib.pyplot as plt
from collections import OrderedDict
from itertools import chain

# Place creation of compartment into function.
def create_compartment(comp_name, comp_length, comp_diameter, RM, CM, RA=1.0):
    ''' Create a compartment
        Input: comp_name -> str
               comp_length -> float
               comp_diameter -> float
    '''
    circum = np.pi * comp_diameter
    curved_sa = circum * comp_length
    x_area = np.pi * comp_diameter ** 2 / 4.0

    comp = moose.Compartment('/'+ comp_name)
    comp.Rm = RM / curved_sa  # RM units are ohm-m^2
    comp.Cm = CM * curved_sa  # CM units are F/m^2
    comp.Ra = RA * comp_length / x_area

    return comp
# Test:  soma = create_compartment('soma', 50E-6, 25E-6, 0.03, 2.8E3, 4.0)

def create_pulse_generator(comp_to_connect, duration, amplitude):
    ''' Create a pulse generator and connect to a moose compartment.
    '''
    pulse = moose.PulseGen('pulse')
    pulse.delay[0] = 50E-3  # First delay.
    pulse.width[0] = duration  # Pulse width.
    pulse.level[0] = amplitude  # Pulse amplitude.
    pulse.delay[1] = 1e9 #Don't start next pulse train.
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

def soma_one_dend():
    soma_l = 50E-6
    soma_d = 25E-6
    soma_RM = 1 #20000
    soma_CM = 10E-3 #1E-6
    soma_RA = 4.0
    simtime = 0.3 # seconds
    simdt = 50E-6 #50E-6 # seconds

    soma = create_compartment('soma', soma_l, soma_d, soma_RM, soma_CM, soma_RA)
    soma_Em = -65E-3
    soma_initVm = -65E-3

    inj_duration = 100E-3
    inj_amplitude = 1E-9 #0.188E-9
    pulse_1 = create_pulse_generator(soma, inj_duration, inj_amplitude)

    vmtab = create_output_table()
    moose.connect(vmtab, 'requestOut', soma, 'getVm')
    moose.showmsg(soma)

    moose.setClock(4, simdt)

    dend1 = create_compartment('dend1',100E-6, 2E-6, soma_RM, soma_CM, soma_RA)
    dend1.Em = soma.Em
    dend1.initVm = soma.initVm
    moose.connect(soma, 'axialOut', dend1, 'handleAxial')
    dend1_vm_tab = create_output_table(table_name='dend1Vm')
    moose.connect(dend1_vm_tab, 'requestOut', dend1, 'getVm')
    moose.showmsg(dend1)

    moose.reinit()
    moose.start(simtime)

    plot_vm_table(vmtab, simtime)
    plot_vm_table(dend1_vm_tab, simtime)
    plt.axvline(x=50E-3 + soma_RM * soma_CM, color='red')
    plt.show()

#soma_one_dend()

def soma_five_dend():
    soma_l = 50E-6
    soma_d = 25E-6
    soma_RM = 1 #20000
    soma_CM = 10E-3 #1E-6
    soma_RA = 4.0
    simtime = 0.3 # seconds
    simdt = 50E-6 #50E-6 # seconds
    dend_n = 5

    soma = create_compartment('soma', soma_l, soma_d, soma_RM, soma_CM, soma_RA)
    soma_Em = -65E-3
    soma_initVm = -65E-3

    inj_duration = 100E-3
    inj_amplitude = 1E-9 #0.188E-9
    pulse_1 = create_pulse_generator(soma, inj_duration, inj_amplitude)

    vmtab = create_output_table()
    moose.connect(vmtab, 'requestOut', soma, 'getVm')
    moose.showmsg(soma)

    moose.setClock(4, simdt)

    bunch = create_n_dends('dend_', dend_n, 100E-6, 2E-6, soma_RM, soma_CM, soma_RA)
    for item in bunch.values():
        item.Em = soma.Em
        item.initVm = soma.initVm
    bunch = connect_n_serial(bunch)
    moose.connect(soma, 'axialOut', list(bunch.values())[0], 'handleAxial')
    dend_vm_tab = create_output_table(table_name='dend3Vm')
    moose.connect(dend_vm_tab, 'requestOut', list(bunch.values())[int(np.median(range(len(bunch))))], 'getVm')

    moose.reinit()
    moose.start(simtime)

    plot = plot_vm_table(simtime, vmtab, dend_vm_tab, title="Soma Vs Dend voltage compare.")
    plot.legend(['soma', 'dend'])
    plt.grid(True)
    plt.show()

#soma_five_dend()

 def compute_comp_area(comp_diameter, comp_length):
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

 def part_a():
 comp_RM = 1
 comp_CM = 10E-3
 comp_RA = 4
 comp_ELEAK = -65E-3
 comp_initVm = -65E-3


 simtime = 300E-3
 simdt = 50E-3

 cell_container = 'chkE19'
 file_name = 'E19-cell_filling-caudal.CNG.swc'

 root_comp = moose.loadModel(file_name, cell_container)

 for comp in moose.wildcardFind(root_comp.path+'/#[TYPE=Compartment]'):
     set_comp_values(comp, comp_RM, comp_CM, comp_RA, comp_initVm, comp_ELEAK)

part_a()
