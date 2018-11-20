
def create_stimulator(h, number, start, interval):
    stim = h.NetStim()
    stim.number = number
    stim.start = start
    stim.interval = interval
    return stim

def connect_stimulator_synapse(h, stim, syn, delay, weight):
    ncstim = h.NetCon(stim, syn)
    ncstim.delay = delay
    ncstim.weight[0] = weight
    return ncstim
