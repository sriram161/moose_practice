import moose
import numpy as np

# place creation of compartment into function

def create_compartment(comp_name, comp_length, comp_diameter, RM, CM, Ra=1.0):
    ''' Create a compartment
        Input: comp_name -> str
               comp_length -> float
               comp_diameter -> float
    '''
    RM = RM*(1E-2)**2  # ohm-m^2
    CM = CM/(1E-2)**2  # F/m^2
    sa = np.pi * comp_diameter
    curved_sa = sa * comp_length
    cross_sa = (np.pi * comp_diameter**2)*1/4
    comp = moose.Compartment('/'+ comp_name)
    comp.Rm = RM / curved_sa
    comp.Cm = CM * curved_sa
    comp.Ra = Ra*comp_length / cross_sa
    comp.diameter = comp_diameter
    comp.length = comp_length
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
    soma_RM = 2.8E3 #20000
    soma_CM = 0.03E-6 #1E-6
    soma_RA = 4.0
    soma = create_compartment('soma', soma_l, soma_d, soma_RM, soma_CM, soma_RA)
    soma.Em = -65E-3
    soma.initVm = -65E-3
    inj_duration = 100E-3
    inj_amplitude = 0.954E-9 #0.188E-9
    pulse_1 = create_pulse_generator(soma, inj_duration, inj_amplitude)
    moose.reinit()
    moose.start(0.3)
    print(soma.Vm)

# Main call.
main()

##### Class Work -3
output = moose.Neutral('/output')
Vmtab = moose.Table('/output/somaVm')
moose.showfield(vmtab)

# To plot tables.
import pylab
t = pylab.linspace(0, 200E-3, len(vmtab.vector))
pylab.plot(t, vmtab.vector)
pylab.show()

# soma data descriptor
soma_l = 20E-6
soma_d = 20E-6

soma_RM = 2 #20000
soma_CM = 0.01 #1E-6
soma_RA = 4.0

# dend data descriptor
dend_l = 40E-6
dend_d = 8E-6
dend_RM = soma_RM
dend_CM = soma_CM
dend_RA = soma_RA

# soma Compartment creation
soma = create_compartment('soma', soma_l, soma_d, soma_RM, soma_CM, soma_RA)
soma.Em = -65E-3
soma.initVm = -65E-3
# dend Compartment creation
dend = create_compartment('dend', dend_l, dend_d, dend_RM, dend_CM, dend_RA)
dend.Em = soma.Em
dend.initVm = soma.initVm

moose.connect(soma, 'axialout', dend, 'handleAxial')
inj_duration = 100E-3
inj_amplitude = 0.954E-9 #0.188E-9
