from ballstick import BallAndStick
from nutil import create_stimulator
from nutil import connect_stimulator_synapse
from collections import namedtuple
from neuron import h
import matplotlib.pyplot as plt

def main():
    settings = {'geometry': (12.6157, 12.6157, 1, 100, 101),
                'biophysics': (100, 1, 0.12, 0.036, 0.0003, -54.3, 0.001, -65)}
    model_1 = BallAndStick(settings)

    # Create synapse on ball and stick model
    prox_syn = model_1.create_syn_on_dend(0.1, 0, 0.1, 20, 1)
    middle_syn = model_1.create_syn_on_dend(0.50,0, 0.1, 20, 1)
    distal_syn = model_1.create_syn_on_dend(1.00,0, 0.1, 20, 1)

    # Create stimulators for synapses
    stim_1 = create_stimulator(1, 5, 1)
    stim_2 = create_stimulator(1, 5, 1)
    stim_3 = create_stimulator(1, 5, 1)

    # Connect stimulators to synapses
    connect_stimulator_synapse(stim_1, prox_syn, delay=5, weight=0.04)
    connect_stimulator_synapse(stim_2, middle_syn, delay=5, weight=0.04)
    connect_stimulator_synapse(stim_3, distal_syn, delay=5, weight=0.04)

    # Create output tables
    t_vec = h.Vector()
    soma_vec = h.Vector()
    prox_vec = h.vector()
    middle_vec = h.Vector()
    distal_vec = h.Vector()
    t_vec.record(h._ref_t)
    soma_vec.record(model_1.soma(0.5)._ref_v)
    prox_vec.record(model_1.dend(0.1)._ref_v)
    middle_vec.record(model_1.dend(0.5)._ref_v)
    distal_vec.record(model_1.dend(1.0)._ref_v)

    # Run simulation
    h.tstop = 40.0
    h.run()

    # plot results
    plt.plot(t_vec, soma_vec, t_vec, prox_vec, t_vec, middle_vec, t_vec, distal_vec)
    plt.show()

            


main()
