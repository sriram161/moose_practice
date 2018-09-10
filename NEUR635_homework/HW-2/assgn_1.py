import moose
import numpy as np 

neuron = moose.Neutral('/neuron')
soma = moose.Compartment('/neuron/soma')

RM = 20E3 # ohm-cm^2
CM = 1E-6 # F/cm^2
Em = -60 # milli volts
initVm = -70 # milli volts

compartment_length = 50 # microns
compartment_diameter = 25 # microns

# Setting values in SI units.

RM = RM*(1E2)**2 # ohm-m^2
CM = CM/(1E2)**2 # F/m^2
Em = Em*1E-3 # Volts
initVm = initVm*1E-3 # Volts
compartment_length = compartment_length*1E-6 # Meters
compartment_diameter = compartment_diameter*1E-6 # Meters

sa = np.pi * compartment_diameter
curved_sa = sa * compartment_length

soma.Rm = RM * curved_sa
soma.Cm = CM / curved_sa
soma.initVm = initVm
soma.Em = Em

# reset simulation 
moose.reinit()

# start simulation at 0 nA injection current.
moose.start(0.3)
moose.showfields(soma) # check Vm


soma.inject = -1E-12
# reset simulation 
moose.reint()
# start simulation at -1pA injection current.
moose.start(0.3)
moose.showfields(soma)
