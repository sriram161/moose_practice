#!/usr/bin/env python3


import logging
from ajustador.helpers.loggingsystem import getlogger
from ajustador.helpers.save_param.create_npz_param import create_npz_param

logger = getlogger(__name__)
logger.setLevel(logging.INFO)



### Test run ###
def test_proto_only():
	npz1 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitFgp-proto-proto144.npz"
	create_npz_param(npz1, model='gp', neuron_type='proto')

def test_proto_and_arky():
	npz1 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitFgp-proto-proto144.npz"
	npz2 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitgp-arky-arky120F.npz"
	create_npz_param(npz1, model='gp', neuron_type='proto')
        create_npz_param(npz2, model='gp', neuron_type='arky', cond_file= 'param_cond_proto144_proto_1954.py')

def test_proto_and_arky(fit_num):
        npz1 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitFgp-proto-proto144.npz"
	npz2 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitgp-arky-arky120F.npz"
	create_npz_param(npz1, model='gp', neuron_type='proto', fitnum = fit_num)
        create_npz_param(npz2, model='gp', neuron_type='arky', cond_file= 'param_cond_proto144_proto_1954.py')

test_proto_only()
