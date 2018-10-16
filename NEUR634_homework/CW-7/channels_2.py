from utilities import AlphaBetaparams
from utilities import CaDepparams
from copy import copy
from utilities import channel_param_template
from utilities import compute_comp_area

EREST_ACT = -70e-3

# CHANNEL: (on membrane)
# Type1 = voltage dependent HH channel <<membrane potentail controls currents>>
# Type2 = calcium dependent voltage channel. <<concentration controls currents>>

# POOLS: (Inside the cell)
# calcium pools are calcium concentration holders inside the cell.

# BUFFERS: (Inside the cell)
# Which controls and maintain concentration inside the cell.
# Eg: Calcium buffers maintain the calcium concentration inside the cell.

Na_m_params = AlphaBetaparams(
              A_A=1e5 * (25e-3 + EREST_ACT), A_B=-1e5, A_C=-1.0, A_D=-25e-3 - EREST_ACT, A_F=-10e-3,
              B_A=4e3, B_B=0.0, B_C=0.0, B_D=0.0 - EREST_ACT, B_F=18e-3)

Na_h_params = AlphaBetaparams(
              A_A=70.0, A_B=0.0, A_C=0.0, A_D=0.0 - EREST_ACT, A_F=0.02,
              B_A=1000.0, B_B=0.0, B_C=1.0, B_D=-30E-3 - EREST_ACT, B_F=-0.01)

K_n_params = AlphaBetaparams(
              A_A=1e4 * (10e-3 + EREST_ACT), A_B=-1e4, A_C=-1.0, A_D=-10e-3 - EREST_ACT, A_F=-10e-3,
              B_A=0.125e3, B_B=0.0, B_C=0.0, B_D=0.0 - EREST_ACT, B_F=80e-3)

ska_param = CaDepparams(kd=0.57E-3, power=5.2, tau=4.9E-3)

Na_chan = copy(channel_param_template)
k_chan = copy(channel_param_template)
ska_chan = copy(channel_param_template)

Na_chan['chan_name']='Na'
Na_chan['x_params']= Na_m_params
Na_chan['y_params']= Na_h_params
Na_chan['x_pow']= 3
Na_chan['y_pow']= 1
Na_chan['g_max']= 120E-3 *compute_comp_area(30e-6, 50e-6)[0] *1E4
#Na_chan['g_max']= 0
Na_chan['e_k']= 115E-3 + EREST_ACT
Na_chan['chan_model'] = 'HHChannel'
Na_chan['chan_model_control'] = 'membrane_voltage'

k_chan['chan_name']= 'K'
k_chan['x_params']= K_n_params
k_chan['x_pow']= 4
k_chan['g_max']= 36e-3 *compute_comp_area(30e-6, 50e-6)[0] *1E4
#k_chan['g_max']= 0
k_chan['e_k']= -12E-3 + EREST_ACT
Na_chan['chan_model'] = 'HHChannel'
Na_chan['chan_model_control'] = 'membrane_voltage'

sk_chan['chan_name']= 'sk'
sk_chan['z_params']= ska_params
sk_chan['z_pow']= 1
sk_chan['g_max']= 36e-3
Na_chan['chan_model'] = 'HHChannel'
Na_chan['chan_model_control'] = 'internal_ion_concentration'

channel_settings = [Na_chan, k_chan, sk_chan]
