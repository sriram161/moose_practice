from copy import copy
from templates import AlphaBetaparams
from templates import CaDepparams
from templates import capools
from templates import channel_param_template
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

sk_z_params = CaDepparams(kd=0.75E-3, power=5.2, tau=4.9E-3)

ca_params = capools(caBasal=50E-6, caThick=1E-6, caTau=20E-3, bufCapacity=20, caName='CaPool')

caL_X_params = AlphaBetaparams(
              A_A=-880, A_B=-220E-3, A_C=-1.0, A_D=4E-3, A_F=-7.5E-3,
              B_A=-284, B_B=71E3, B_C=-1.0, B_D=-4E-3, B_F=5e-3)

Na_chan = copy(channel_param_template)
k_chan = copy(channel_param_template)
SKca_chan = copy(channel_param_template)
CaL_chan = copy(channel_param_template)

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

SKca_chan['chan_name'] = 'SKca'
SKca_chan['z_params'] = sk_z_params
SKca_chan['z_pow'] = 1
SKca_chan['g_max'] = 2E-6 *compute_comp_area(30e-6, 50e-6)[0] *1E4
SKca_chan['g_max'] = 0
SKca_chan['e_k'] = -87E-3
SKca_chan['chan_type'] = 'ca_dependent'

CaL_chan['chan_name'] = 'CaL'
CaL_chan['x_params'] =  caL_X_params
CaL_chan['x_pow'] = 1
CaL_chan['g_max'] = 1E-2 *compute_comp_area(30e-6, 50e-6)[0] *1E4
CaL_chan['g_max'] = 0
CaL_chan['e_k'] = 130e-3
CaL_chan['chan_type'] = 'ca_permeable'

# define calcium channel
# channel_settings = [Na_chan, k_chan] # working good!!!
# channel_settings = [Na_chan, k_chan, CaL_chan]
#channel_settings = [Na_chan, k_chan, SKca_chan]
channel_settings = [Na_chan, k_chan, SKca_chan, CaL_chan]

channel_settings = {chan.get('chan_name'): chan for chan in channel_settings}
