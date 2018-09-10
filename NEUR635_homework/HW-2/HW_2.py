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
    comp_length = comp_length*1E-6  # Meters
    comp_diameter = comp_diameter*1E-6  # Meters
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
    pulse.delay[0] = 10E-3  # First delay.
    pulse.width[0] = duration  # Pulse width.
    pulse.level[0] = amplitude  # Pulse amplitude.
    moose.connect(pulse, 'output', comp_to_connect, 'injectMsg')
    return pulse
# Test: pulse_1 = create_pulse_generator( soma, 100E-3, 1E-9)


soma_l = 50E-6
soma_d = 25E-6
soma_RM = 100 #0.03
soma_CM = 1 #2.8E3
soma_RA = 4.0

soma = create_compartment('soma', soma_l, soma_d, soma_RM, soma_CM, soma_RA)

inj_duration = 200E-3
inj_amplitude = 10E-3
pulse_1 = create_pulse_generator(soma, inj_duration, inj_amplitude)
moose.showfields(soma)

   # Goal: set cell potential at 30mV.

for inj in np.linspace(1E-9, 100E-9,10):
    moose.reinit()
    pulse_1 = create_pulse_generator(soma, inj_duration, inj)
    moose.start(0.3)
    print(soma.Vm)

for inj in np.linspace(1E-9, 10,1000):
    moose.reinit()
    soma.inject = inj
    moose.start(0.3)
    print(soma.Vm)
