import moose
import numpy as np
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

def create_swc_comp():
 comp_RM = 1
 comp_CM = 10E-3
 comp_RA = 4
 comp_ELEAK = -65E-3
 comp_initVm = -65E-3
 cell_container = 'chkE19'
 file_name = 'E19-cell_filling-caudal.CNG.swc'

 root_comp = moose.loadModel(file_name, cell_container)

 for comp in moose.wildcardFind(root_comp.path+'/#[TYPE=Compartment]'):
     set_comp_values(comp, comp_RM, comp_CM, comp_RA, comp_initVm, comp_ELEAK)
 return root_comp

def create_p_comp():
    cell_container_p = 'corcell'
    file_name = 'layer2.p'
    root_comp = moose.loadModel(file_name, cell_container_p)
    return root_comp

def sim_run():
    simtime = 1000E-3
    simdt = 0.5E-3
    inj_duration = 50E-3
    inj_amplitude = 0.1E-12

    # Create cell
    chicken_cell = create_swc_comp()
    cortical_cell = create_p_comp()
    chicken_cell_soma = moose.element('/chkE19[0]/soma')
    cortical_cell_soma = moose.element('/corcell[0]/soma')

    #Create injection source
    chicken_inject = create_pulse_generator(chicken_cell_soma, inj_duration, inj_amplitude)
    cortical_inject = create_pulse_generator(cortical_cell_soma, inj_duration, inj_amplitude)

    # Create output tables
    chicken_soma_table = create_output_table(table_element='/output', table_name='chksoma')
    chicken_dend_table = create_output_table(table_element='/output', table_name='chkdend')
    cortical_soma_table = create_output_table(table_element='/output', table_name='corsoma')
    cortical_dend_table = create_output_table(table_element='/output', table_name='cordend')

    # Connect output tables to target compartments.
    moose.connect(chicken_soma_table, 'requestOut', chicken_cell_soma, 'getVm')
    moose.connect(cortical_soma_table, 'requestOut', cortical_cell_soma, 'getVm')
    moose.connect(chicken_dend_table, 'requestOut', moose.element('/chkE19[0]/dend_36_0'), 'getVm')
    moose.connect(cortical_dend_table, 'requestOut', moose.element('/corcell[0]/apical3'), 'getVm')

    # Set moose simulation clocks
    for lable in range(7):
        moose.setClock(lable, simdt)

    # Run simulation
    moose.reinit()
    moose.start(simtime)

    plot_chk = plot_vm_table(simtime, chicken_soma_table, chicken_dend_table, title="Chicken Cell")
    plot_chk.legend(['soma', 'dend'])
    plot_cor = plot_vm_table(simtime, cortical_soma_table, cortical_dend_table, title="cortical Cell")
    plot_cor.legend(['soma', 'dend'])
    plt.grid(True)
    plt.show()

sim_run()
