import moose
import numpy as np
import math

# Converted everything into SI units.
rm = 2/10E-4
cm = 1E-6/10E-4
Em = -0.065

# length is 100 microns, radius is 10 microns.
Rm = rm*(2*math.pi*10E-6*100E-6)
Cm = cm/(2*math.pi*10E-6*100E-6)  # not understand calc using equation. :(

soma = moose.Compartment('/soma')
soma.setRm(Rm)
soma.setCm(Cm)
soma.setEm(Em)

print(soma.Rm, soma.Cm, soma.Em)
moose.showfield(soma)

#Part 2  Create a pulse gen
pulse = moose.PulseGen('pulse')
duration = 200E-3
Vm = 30E-3
I_inj = (Vm-Em)/Rm + Vm/duration
pulse.setFirstDelay(50E-3)
pulse.setFirstWidth(duration)
pulse.setFirstLevel(I_inj)
pulse.setCount(1)
moose.showfield(pulse)

# I didnot understand what is difference between tick and count :(

#Part 3 Connect pulse generator with soma.
connected = moose.connect(pulse,'output' , soma, 'injectMsg')
moose.showfield(connected)
print(connected.e2[0].Rm)
