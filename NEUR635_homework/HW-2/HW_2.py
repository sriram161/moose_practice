import moose
import numpy as np

# place creation of compartment into function

def create_compartment(comp_name, comp_length, comp_diameter, RM, CM, Ra=0):
    ''' Create a compartment
        Input: comp_name -> str
               comp_length -> float
               comp_diameter -> float
    '''
    RM = RM*(1E2)**2  # ohm-m^2
    CM = CM/(1E2)**2  # F/m^2
    sa = np.pi * comp_diameter
    curved_sa = sa * comp_length
    comp = moose.Compartment('/'+ comp_name)
    comp.Rm = RM * curved_sa
    comp.Cm = CM / curved_sa
    comp.Ra = Ra if Ra !=0 else 1.0
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

def main():
    soma_l = 50E-6
    soma_d = 25E-6
    soma_RM = 20000 #0.03
    soma_CM = 1.0 #2.8E3
    soma_RA = 4.0
    soma = create_compartment('soma', soma_l, soma_d, soma_RM, soma_CM, soma_RA)
    soma.Em = -65E-3
    soma.initVm = -65E-3
    inj_duration = 100E-3
    inj_amplitude = 1E-9
    pulse_1 = create_pulse_generator(soma, inj_duration, inj_amplitude)
    moose.reinit()
    moose.start(0.3)
    print(soma.Vm)

main()
