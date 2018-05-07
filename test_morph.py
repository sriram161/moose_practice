#!/usr/bin/env python3


import logging
from ajustador.helpers.loggingsystem import getlogger
from ajustador.helpers.save_param.create_npz_param import create_npz_param

logger = getlogger(__name__)
logger.setLevel(logging.INFO)

npz1 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitFgp-proto-proto144.npz"
npz2 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitd1d2-D1-D1_010612_pas3.npz"
npz3 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitgp-arky-arky120F.npz"
store_param_path = "/home/ram/neural_prj/outputs/parameter_sets"

### Test run ###
create_npz_param(npz2, model='d1d2', neuron_type='D1')
create_npz_param(npz1, model='gp', neuron_type='proto')
create_npz_param(npz2, model='d1d2', neuron_type='D1', store_param_path=store_param_path)
create_npz_param(npz1, model='gp', neuron_type='proto', fitnum=10, store_param_path=store_param_path)
create_npz_param(npz3, model='gp', neuron_type='arky', cond_file= 'param_cond_proto_1954.py')
create_npz_param(npz3, model='gp', neuron_type='arky',fitnum = 20, cond_file= 'param_cond_proto_1954_arky_1585.py')
create_npz_param(npz1, model='gp', neuron_type='proto',fitnum = 55, cond_file= 'param_cond_proto_1954_arky_1585.py')
