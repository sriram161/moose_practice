from collections import namedtuple

AlphaBetaparams = namedtuple('AlphaBetaparams', 'A_A A_B A_C A_D A_F B_A B_B B_C B_D B_F')

CaDepparams = namedtuple('caDepparams', 'kd power tau')

channel_param_template = {'chan_name':None, 'x_params': None, 'y_params': None, 'z_params': None,
                          'x_pow': None, 'y_pow': None, 'z_pow': None,
                          'g_max': None, 'ek': None, 'chan_type': None}

capools = namedtuple('caparams', 'caBasal caThick caTau bufCapacity caName')

SynapseChannel = namedtuple('SynapseChannel', 'syn_name g_max tau1 tau2 ek synapse_count delay params')

nmdamgblock = namedtuple('nmdamgblock', 'A B conc temperature extca condfraction')
