
import moose
from utilities import *

spikegen = moose.SpikeGen('spikegen')
spikegen.threshold=0
spikegen.refractT=1E-3

length = 50E-6
diameter = 25E-6
RM = 1 #20000
CM = 10E-3 #1E-6
RA = 4.0
EREST_ACT = -65E-3
Em = -65E-3

simtime = 0.3 # seconds
simdt = 50E-6 #50E-6 # seconds

soma = create_compartment('soma', length, diameter, RM, CM, initVM=EREST_ACT, ELEAK=Em)
dend = create_compartment('dend', length, diameter, RM, CM, initVM=EREST_ACT, ELEAK=Em)

synchan = moose.SynChan('glu')
synchan.Gbar = 1E-8
synchan.tau1 = 2E-3
synchan.tau2 = 2E-3
synchan.Ek = -10E-3

# Connections

moose.connect(soma, 'axialOut', dend, 'handleAxial')
moose.connect(dend, 'channel', synchan, 'channel')

sh = moose.SimpleSynHandler(synchan.path + '/synhandler')

moose.connect(sh, 'activationOut', synchan, 'activation')
sh.synapse.num = 1
sh.synapse[0].delay = 1E-3
moose.showmsg(sh)

presyn = moose.RandSpike('presyn_input')
presyn.rate = 1.3
presyn.refractT = 1E-3
moose.connect(presyn, 'spikeOut', sh.synapse[0], 'addSpike')

sh.synapse.num = 2
sh.synapse[1].delay = 0.1E-3

presyn2 = moose.RandSpike('presyn_input2')
presyn2.rate = 3.5
presyn2.refractT = 1E-3
moose.connect(presyn2, 'spikeOut', sh.synapse[1], 'addSpike')

spiketable1 = moose.Table('spikes1')
moose.connect(presyn, 'spikeOut', spiketable1, 'spike')
spiketable2 = moose.Table('spikes2')
moose.connect(presyn2, 'spikeOut', spiketable2, 'spike')

moose.showmsg(spiketable1)
moose.showmsg(spiketable2)

simdt = 10E-5
plotdt = 10E-5
for lable in range(10):
    moose.setClock(lable, simdt)
moose.setClock(8, plotdt)

soma_v_table = create_output_table(table_element='/output', table_name='somaVm')

for rate1, rate2 in [(1, 10), (1,0)]:
    presyn.rate = rate1
    presyn2.rate = rate2
    v_plot = plot_vm_table(simtime, soma_v_table)
    moose.reinit()
    moose.start(1)
