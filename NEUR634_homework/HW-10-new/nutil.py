from neuron import h

def create_stimulator(number, start, interval):
    stim = h.NetStim()
    stim.number = number
    stim.start = start
    stim.interval = interval
    return stim

def connect_stimulator_synapse(stim, syn, delay, weight):
    import pdb; pdb.set_trace()
    ncstim = h.NetCon(stim, syn)
    ncstim.delay = delay
    ncstim.weight[0] = weight
    return ncstim
