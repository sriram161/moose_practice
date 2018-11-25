from copy import copy
from templates import AlphaBetaparams
from templates import SynapseChannel
from templates import channel_param_template
from templates import capools
from templates import nmdamgblock
from utilities import compute_comp_area

EREST_ACT = -70e-3

Na_m_params = AlphaBetaparams(
              A_A=1e5 * (25e-3 + EREST_ACT), A_B=-1e5, A_C=-1.0, A_D=-25e-3 - EREST_ACT, A_F=-10e-3,
              B_A=4e3, B_B=0.0, B_C=0.0, B_D=0.0 - EREST_ACT, B_F=18e-3)

Na_h_params = AlphaBetaparams(
              A_A=70.0, A_B=0.0, A_C=0.0, A_D=0.0 - EREST_ACT, A_F=0.02,
              B_A=1000.0, B_B=0.0, B_C=1.0, B_D=-30E-3 - EREST_ACT, B_F=-0.01)

K_n_params = AlphaBetaparams(
              A_A=1e4 * (10e-3 + EREST_ACT), A_B=-1e4, A_C=-1.0, A_D=-10e-3 - EREST_ACT, A_F=-10e-3,
              B_A=0.125e3, B_B=0.0, B_C=0.0, B_D=0.0 - EREST_ACT, B_F=80e-3)

ca_params = capools(caBasal=50E-6, caThick=1E-6, caTau=20E-3, bufCapacity=20, caName='CaPool')


AMPA = SynapseChannel(syn_name='ampa', g_max=1E-8, tau1=1E-3, tau2=5E-3, ek=0, synapse_count=1, delay=1E-3, params=None) # Excitatory synapses
GABA = SynapseChannel(syn_name='gaba', g_max=1E-8, tau1=0.5E-3, tau2=5.5E-3, ek=-80E-3, synapse_count=1, delay=1E-3, params=None) # Inhabitory sunapses

mgblockparams = nmdamgblock(A=(1/6.0) ,B=(1/80.0) ,conc=1.4 ,temperature=303 ,extca=2 ,condfraction=0.1)

NMDA = SynapseChannel(syn_name='nmda', g_max=2E-9, tau1=1.1E-3, tau2=37.5E-3, ek=5E-3, synapse_count=1, delay=1E-3, params=mgblockparams)

Na_chan = copy(channel_param_template)
k_chan = copy(channel_param_template)

Na_chan['chan_name'] = 'Na'
Na_chan['x_params'] = Na_m_params
Na_chan['y_params'] = Na_h_params
Na_chan['x_pow'] = 3
Na_chan['y_pow'] = 1
Na_chan['g_max'] = 120E-3 *compute_comp_area(30e-6, 50e-6)[0] *1E4
Na_chan['e_k'] = 115E-3 + EREST_ACT

k_chan['chan_name'] = 'K'
k_chan['x_params'] = K_n_params
k_chan['x_pow'] = 4
k_chan['g_max'] = 36e-3 *compute_comp_area(30e-6, 50e-6)[0] *1E4
k_chan['e_k'] = -12E-3 + EREST_ACT

channel_settings = [Na_chan, k_chan]
synapse_settings2 = [AMPA, GABA, NMDA]

channel_settings = {chan.get('chan_name'): chan for chan in channel_settings}
