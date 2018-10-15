from utilities import AlphaBetaparams
from copy import copy
from utilities import channel_param_template
from utilities import compute_comp_area

EREST_ACT = -70e-3

K_n_params = AlphaBetaparams(
              A_A=1, A_B=0, A_C=1.0, A_D=-20E-3, A_F=4e-3,
              B_A=1, B_B=0.0, B_C=1.0, B_D= -20E-3, B_F=4e-3)

k_chan = copy(channel_param_template)

k_chan['chan_name']= 'K'
k_chan['x_params']= K_n_params
k_chan['x_pow']= 4 # Given in paper for voltage-gated potassium channel K is 4 and others k=1.
#k_chan['g_max']= 36e-3 * compute_comp_area(30e-6, 50e-6)[0] *1E4
k_chan['g_max']= 0 #0.5  * compute_comp_area(30e-6, 50e-6)[0] *1E4
k_chan['e_k']= -90E-3

channel_settings = [k_chan]

# Given Tau is 200ms with C = 1E-6 F/cm2  i.e. C = 1E-2 F/m2 
# R = 20
# http://neuromorpho.org/neuron_info.jsp?neuron_name=ACC1 striatum medium spiny projection neuron.
# http://neuromorpho.org/dableFiles/martone/CNG%20version/ACC1.CNG.swc


# 