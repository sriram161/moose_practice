# Try it on zeus.vse.gmu.edu
import moose
help(moose)
dir(moose)
moose.le('/classes')
moose.doc(moose.Compartment)
help(moose.Compartment)

moose.le()

soma = moose.Compartment('soma')
soma = moose.element('soma') # Returns a refence to an existant moose element.
# Doesn't create new moose element.!!!

neuron = moose.Neutral('/neuron')
soma = moose.Compartment('/neuron/soma')
dend = moose.Compartment('/neuron/dend')
data = moose.Neutral('/data')

print soma.path
print soma.name

# List elements under a moose element.
moose.le('/neuron')

# List all the attributes of a moose element.
moose.showfield('/neuron')

# Print individual attributes of moose elements to examine.
print soma.Rm, soma.Vm, soma.Cm, soma.Ra

# Allows moose to traverse into moose element to short showfield command.
moose.ce('/neuron') # Change head node element for traversal.
moose.ce(neuron)
moose.ce() # Change the head node to root node.

soma.Cm = 1e-9
soma.Rm = 10e6
soma.initVm = -75E-3


