#!/usr/bin/env python3

import sys
import logging
from ajustador.helpers.loggingsystem import getlogger
from ajustador.helpers.save_param.create_npz_param import create_npz_param

logger = getlogger(__name__)
logger.setLevel(logging.INFO)

### Test run ###
def test_proto_only(npz1):
    create_npz_param(npz1, model='gp', neuron_type='proto')

def test_proto_and_arky(npz1, npz2):
    create_npz_param(npz1, model='gp', neuron_type='proto')
    create_npz_param(npz2, model='gp', neuron_type='arky', cond_file= 'param_cond_proto144_proto_1954.py')

def test_proto_and_arky_fit(npz1, npz2, fit_num):
    create_npz_param(npz1, model='gp', neuron_type='proto', fitnum = fit_num)
    create_npz_param(npz2, model='gp', neuron_type='arky', fitnum= fit_num,
                     cond_file= 'param_cond_proto144_proto_10.py')

if __name__ == "__main__":
        npz2 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitgp-arky-arky120F.npz"
        npz1 = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitFgp-proto-proto144.npz"
        fitnum = 10
        if sys.argv[1] == '1':
            test_proto_only(npz1)
        elif sys.argv[1] == '2':
            test_proto_and_arky(npz1, npz2)
        elif sys.argv[1] == '3':
            test_proto_and_arky_fit(npz1, npz2, fitnum)
        else:
            print("Options Proto_only : 1 \n Proto_and_arky : 2 \n Proto_and_arky with fitnum = 10 : 3")
