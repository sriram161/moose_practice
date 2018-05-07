
import numpy as np
import matplotlib.pyplot as plt
import moose
from collections import namedtuple

Chn_param = namedtuple("params", "A_A A_B A_C A_D A_F B_A B_B B_C B_D B_F VDIVS VMIN VMAX".split())

EREST_ACT = -70e-3 #: Resting membrane potential

#: The parameters for defining m as a function of Vm
Na_m_params = [1e5 * (25e-3 + EREST_ACT),   # 'A_A':
                -1e5,                       # 'A_B':
                -1.0,                       # 'A_C':
                -25e-3 - EREST_ACT,         # 'A_D':
               -10e-3,                      # 'A_F':
               4e3,                     # 'B_A':
                0.0,                        # 'B_B':
                0.0,                        # 'B_C':
                0.0 - EREST_ACT,            # 'B_D':
                18e-3                       # 'B_F':
               ]

#: Parameters for defining h gate of Na+ channel
Na_h_params = [ 70.0,                        # 'A_A':
                0.0,                       # 'A_B':
                0.0,                       # 'A_C':
                0.0 - EREST_ACT,           # 'A_D':
                0.02,                     # 'A_F':
                1000.0,                       # 'B_A':
                0.0,                       # 'B_B':
                1.0,                       # 'B_C':
                -30e-3 - EREST_ACT,        # 'B_D':
                -0.01                    # 'B_F':
                ]

#: K+ channel in Hodgkin-Huxley model has only one gate, n and these
#are the parameters for the same
K_n_params = [ 1e4 * (10e-3 + EREST_ACT),   #  'A_A':
               -1e4,                      #  'A_B':
               -1.0,                       #  'A_C':
               -10e-3 - EREST_ACT,         #  'A_D':
               -10e-3,                     #  'A_F':
               0.125e3,                   #  'B_A':
               0.0,                        #  'B_B':
               0.0,                        #  'B_C':
               0.0 - EREST_ACT,            #  'B_D':
               80e-3                       #  'B_F':
               ]

#: We define the rate parameters, which are functions of Vm as
#: interpolation tables looked up by membrane potential.
#: Minimum x-value for the interpolation table
VMIN = -30e-3 + EREST_ACT
#: Maximum x-value for the interpolation table
VMAX = 120e-3 + EREST_ACT
#: Number of divisions in the interpolation table
VDIVS = 3000

Na_m_params = Chn_param(*Na_m_params, VDIVS, VMIN, VMAX)
Na_h_params = Chn_param(*Na_h_params, VDIVS, VMIN, VMAX)
K_n_params = Chn_param(*K_n_params, VDIVS, VMIN, VMAX)

def create_HHChannel_proto(ion, tick, xpower, m_params, ypower=None, h_params=None):
    """ Need m_params and h_params for sodium channel and
        only m_params for potassium channel.
    """
    global VDIVS, VMIN, VMAX
    lib = moose.Neutral('/library')
    hhchannel = moose.HHChannel('/library/'+ion)
    hhchannel.tick = tick
    hhchannel.Xpower = xpower
    xGate = moose.element(hhchannel.path + '/gateX')
    xGate.setupAlpha(m_params)

    if ypower:
        hhchannel.Ypower = ypower
        yGate = moose.element(hhchannel.path + '/gateY')
        yGate.setupAlpha(h_params)
    return hhchannel


def create_1comp_neuron(path, number=1):
    """Create single-compartmental neuron with Na+ and K+ channels.

    Parameters
    ----------
    path : str
        path of the compartment to be created

    number : int
        number of compartments to be created. If n is greater than 1,
        we create a vec with that size, each having the same property.

    Returns
    -------
    comp : moose.Compartment
        a compartment vec with `number` elements.

    """
    global Na_h_params, Na_m_params, K_n_params
    comps = moose.vec(path=path, n=number, dtype='Compartment')
    diameter = 30e-6
    length = 50e-6
    sarea = np.pi * diameter * length
    xarea = np.pi * diameter * diameter / 4.0
    Em = EREST_ACT + 10.613e-3
    comps.Em = Em
    comps.initVm = EREST_ACT
    #: CM = 1 uF/cm^2
    comps.Cm = 1e-6 * sarea * 1e4
    #: RM = 0.3 mS/cm^2
    comps.Rm = 1 / (0.3e-3 * sarea * 1e4)
    container = comps[0].parent.path
    #: Here we create copies of the prototype channels
    na_chn = create_HHChannel_proto(ion='na', tick=-1, xpower=3, m_params=Na_m_params,
    ypower=1, h_params=Na_h_params)
    k_chn = create_HHChannel_proto(ion='k', tick=-1, xpower=4, m_params=K_n_params)
    nachan = moose.copy(na_chn, container, 'na_{}'.format(comps.name), number)
    #: Gbar_Na = 120 mS/cm^2
    nachan.Gbar = [120e-3 * sarea * 1e4] * len(nachan)
    nachan.Ek = 115e-3 + EREST_ACT
    moose.connect(nachan, 'channel', comps, 'channel', 'OneToOne')
    kchan = moose.copy(k_chn, container, 'k_{}'.format(comps.name), number)
    #: Gbar_K = 36 mS/cm^2
    kchan.Gbar = 36e-3 * sarea * 1e4
    kchan.Ek = -12e-3 + EREST_ACT
    moose.connect(kchan, 'channel', comps, 'channel', 'OneToOne')
    return comps


def current_step_test(simtime, simdt, plotdt):
    """Create a single compartment and set it up for applying a step
    current injection.

    We use a PulseGen object to generate a 40 ms wide 1 nA current
    pulse that starts 20 ms after start of simulation.

    """
    model = moose.Neutral('/model')
    comp = create_1comp_neuron('/model/neuron')
    stim = moose.PulseGen('/model/stimulus')
    stim.delay[0] = 20e-3
    stim.level[0] = 1e-9
    stim.width[0] = 40e-3
    stim.delay[1] = 1e9
    moose.connect(stim, 'output', comp, 'injectMsg')
    data = moose.Neutral('/data')
    current_tab = moose.Table('/data/current')
    moose.connect(current_tab, 'requestOut', stim, 'getOutputValue')
    vm_tab = moose.Table('/data/Vm')
    moose.connect(vm_tab, 'requestOut', comp, 'getVm')
    for i in range(10):
        moose.setClock(i, simdt)
    moose.setClock(8, plotdt)
    moose.reinit()
    moose.start(simtime)
    ts = np.linspace(0, simtime, len(vm_tab.vector))
    return ts, current_tab.vector, vm_tab.vector,


if __name__ == '__main__':
    simtime = 0.1
    simdt = 0.25e-5
    plotdt = 0.25e-3
    ts, current, vm = current_step_test(simtime, simdt, plotdt)
    plt.plot(ts, vm * 1e3, label='Vm (mV)')
    plt.plot(ts, current * 1e9, label='current (nA)')
    plt.legend()
    plt.show()
