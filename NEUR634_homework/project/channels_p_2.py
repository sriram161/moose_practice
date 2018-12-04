from copy import copy
from templates import AlphaBetaparams
from templates import channel_param_template
from templates import capools
from templates import CaDepparams

# Old parameters used to setup alpha and beta parameters.
K_n_params = AlphaBetaparams(
              A_A=1000, A_B=0.0, A_C=1.0, A_D=20E-3, A_F=-4e-3,
              B_A=1000, B_B=0.0, B_C=1.0, B_D=20E-3, B_F=4e-3)

ca_v1_params = AlphaBetaparams(
              A_A=1000, A_B=0.0, A_C=1.0, A_D=10E-3, A_F=-15e-3,
              B_A=1000, B_B=0.0, B_C=1.0, B_D=10E-3, B_F=15e-3)

ca_v2_params = AlphaBetaparams(
              A_A=1000, A_B=0.0, A_C=1.0, A_D=-10E-3, A_F=-15e-3,
              B_A=1000, B_B=0.0, B_C=1.0, B_D=-10E-3, B_F=15e-3)

ca_cc_params = CaDepparams(kd=1E-3, power=2, tau=0.68E-2) # After discussion.
#Where is Kd, power and tau??
ca_params = capools(caBasal=0, caThick=0.1E-6, caTau=20E-3, bufCapacity=10E4, caName='CaPool') #0.99E12
### ca_params = capools(caBasal=0, caThick=0.1E-6, caTau=20E-3, bufCapacity=10E4, caName='CaPool') #0.99E12 oscillation
# CaThick, cabasal and tau of ca_cc leave default.
# Tp = 200 ms, ka = 1000 uM, buf=0.6

EREST_ACT = -70E-3
Na_m_params = AlphaBetaparams(A_A=9738.024807333182,
 A_B=0.0,
 A_C=1,
 A_D=0.04155939062329942,
 A_F=-0.005,
 B_A=9738.024807333182,
 B_B=0.0,
 B_C=1,
 B_D=0.04155939062329942,
 B_F=0.005)

Na_h_params = AlphaBetaparams(A_A=2434.5062018332956,
 A_B=0.0,
 A_C=1,
 A_D=0.07755939062329942,
 A_F=0.009,
 B_A=2434.5062018332956,
 B_B=0.0,
 B_C=1,
 B_D=0.037559390623299424,
 B_F=-0.005)

k_chan = copy(channel_param_template)
ca_v1_chan = copy(channel_param_template)
ca_v2_chan = copy(channel_param_template)
ca_cc_chan = copy(channel_param_template)
Na_chan = copy(channel_param_template)

k_chan['chan_name'] = 'K'
k_chan['x_params'] = K_n_params
k_chan['x_pow'] = 4
k_chan['g_max'] = 0.5e-3 * 1/1E4 # was 0
k_chan['e_k'] = -90E-3

ca_v1_chan['chan_name'] = 'Ca_V1'
ca_v1_chan['x_params'] = ca_v1_params
ca_v1_chan['x_pow'] = 1
ca_v1_chan['g_max'] = 0.18E-3 * 1/1E4
ca_v1_chan['e_k'] = 100E-3
ca_v1_chan['chan_type'] = 'ca_permeable'

ca_v2_chan['chan_name'] = 'Ca_V2'
ca_v2_chan['x_params'] = ca_v2_params
ca_v2_chan['x_pow'] = 1
ca_v2_chan['g_max'] = 0.4E-3  * 1/1E4
ca_v2_chan['e_k'] = 100E-3
ca_v2_chan['chan_type'] = 'ca_permeable'

ca_cc_chan['chan_name'] = 'ca_cc'
ca_cc_chan['z_params'] = ca_cc_params
ca_cc_chan['z_pow'] = 1
ca_cc_chan['g_max'] = 40E-3  * 1/1E4 # In paper that is a typo gL instead of gCl.
ca_cc_chan['e_k'] = -70E-3
ca_cc_chan['chan_type'] = 'ca_dependent'

Na_chan['chan_name'] = 'Na'
Na_chan['x_params'] = Na_m_params
Na_chan['y_params'] = Na_h_params
Na_chan['x_pow'] = 3
Na_chan['y_pow'] = 1
Na_chan['g_max'] = 120E-3
Na_chan['e_k'] = 45E-3

channel_settings = [k_chan, ca_v1_chan, ca_v2_chan, ca_cc_chan, Na_chan]

channel_settings = {chan.get('chan_name'): chan for chan in channel_settings}
