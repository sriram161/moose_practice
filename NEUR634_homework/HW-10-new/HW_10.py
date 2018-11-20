import numpy as np
from ballstick import BallAndStick
from nutil import create_stimulator
from nutil import connect_stimulator_synapse
from collections import namedtuple
from neuron import gui, h
import matplotlib.pyplot as plt


def main(prox_flag, middle_flag, distal_flag, prox_w, middle_w, distal_w):
    settings = {'geometry': (12.6157, 12.6157, 1, 100, 101),
                'biophysics': (100, 1, 0.12, 0.036, 0.0003, -54.3, 0.001, -65)}
    model_1 = BallAndStick(settings)

    # Create synapse on ball and stick model
    prox_syn = model_1.create_syn_on_dend(0.1, 0, 1)
    middle_syn = model_1.create_syn_on_dend(0.50,0, 1)
    distal_syn = model_1.create_syn_on_dend(1.00,0, 1)

    # Create stimulators for synapses
    stim_1 = create_stimulator(h, 1, 5, 10)
    stim_2 = create_stimulator(h, 1, 5, 10)
    stim_3 = create_stimulator(h, 1, 5, 10)

    # Connect stimulators to synapses
    if int(prox_flag):
        connect_stimulator_synapse(h, stim_1, prox_syn, delay=5, weight=np.float32(prox_w))
    if int(middle_flag):
        connect_stimulator_synapse(h, stim_2, middle_syn, delay=5, weight=np.float32(middle_w))
    if int(distal_flag):
        connect_stimulator_synapse(h, stim_3, distal_syn, delay=5, weight=np.float32(distal_w))

    # Create output tables
    t_vec = h.Vector()
    soma_vec = h.Vector()
    prox_vec = h.Vector()
    middle_vec = h.Vector()
    distal_vec = h.Vector()
    t_vec.record(h._ref_t)
    soma_vec.record(model_1.soma(0.5)._ref_v)
    prox_vec.record(model_1.dend(0.1)._ref_v)
    middle_vec.record(model_1.dend(0.5)._ref_v)
    distal_vec.record(model_1.dend(1.0)._ref_v)

    # Run simulation
    h.tstop = 400
    h.run()

    # plot results
    plt.plot(t_vec, soma_vec, t_vec, prox_vec, t_vec, middle_vec, t_vec, distal_vec)
    plt.legend(['soma', 'prox', 'middle', 'distal'])
    plt.show()

if __name__ == '__main__':
    import sys
    main(prox_flag=sys.argv[1], middle_flag=sys.argv[2], distal_flag=sys.argv[3],
         prox_w=sys.argv[4], middle_w=sys.argv[5], distal_w=sys.argv[6])


# python HW_10.py 0 0 0 0.04 0.04 0.04
# python HW_10.py 1 0 0 0.04 0.04 0.04
# python HW_10.py 1 1 0 0.04 0.04 0.04
# python HW_10.py 1 1 1 0.04 0.04 0.04


