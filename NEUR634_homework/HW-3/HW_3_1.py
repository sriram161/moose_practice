import moose
import numpy as np
import matplotlib.pyplot as plt

# Place creation of compartment into function.
def create_compartment(comp_name, comp_length, comp_diameter, RM, CM, Ra=1.0):
    ''' Create a compartment
        Input: comp_name -> str
               comp_length -> float
               comp_diameter -> float
    '''
    circum = np.pi * comp_diameter
    curved_sa = circum * comp_length

    comp = moose.Compartment('/'+ comp_name)
    comp.Rm = RM / curved_sa  # RM units are ohm-m^2
    comp.Cm = CM * curved_sa  # CM units are F/m^2
    comp.Ra = Ra

    return comp
# Test:  soma = create_compartment('soma', 50E-6, 25E-6, 0.03, 2.8E3, 4.0)

def create_pulse_generator(comp_to_connect, duration, amplitude):
    ''' Create a pulse generator and connect to a moose compartment.
    '''
    pulse = moose.PulseGen('pulse')
    pulse.delay[0] = 50E-3  # First delay.
    pulse.width[0] = duration  # Pulse width.
    pulse.level[0] = amplitude  # Pulse amplitude.
    moose.connect(pulse, 'output', comp_to_connect, 'injectMsg')
    return pulse

# Test: pulse_1 = create_pulse_generator( soma, 100E-3, 1E-9)

def create_output_table(table_element='/output', table_name='somaVm'):
    ''' Creates and returns a moose table element.
    '''
    output = moose.Neutral(table_element)
    membrane_voltage_table = moose.Table('/'.join((table_element, table_name)))
    return membrane_voltage_table

def plot_vm_table(compartment, simtime):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(0, simtime)
    ax.plot(compartment.vector)
    plt.grid(True)
    plt.show()

def main():
    soma_l = 50E-6
    soma_d = 25E-6
    soma_RM = 1 #20000
    soma_CM = 10E-3 #1E-6
    soma_RA = 4.0
    simtime = 0.3 # seconds
    simdt = 5E-3 #50E-6 # seconds

    soma = create_compartment('soma', soma_l, soma_d, soma_RM, soma_CM, soma_RA)
    soma.Em = -65E-3
    soma.initVm = -65E-3

    inj_duration = 100E-3
    inj_amplitude = 1E-9 #0.188E-9
    pulse_1 = create_pulse_generator(soma, inj_duration, inj_amplitude)

    vmtab = create_output_table()
    moose.connect(vmtab, 'requestOut', soma, 'getVm')
    moose.showmsg(soma)

    moose.setClock(4, simdt)

    moose.reinit()
    moose.start(simtime)

    plot_vm_table(vmtab, simtime)

main()
