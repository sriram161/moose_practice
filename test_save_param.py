#!/usr/bin/env python3

import logging
import shutil
from ajustador.helpers.loggingsystem import getlogger
from ajustador.helpers.save_param.save_param_npz import save_param_npz

logger = getlogger(__name__)
logger.setLevel(logging.INFO)

npz = "/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitFgp-proto-proto144.npz"
store_param_path = "/home/ram/neural_prj/outputs/parameter_sets"
shutil.rmtree(store_param_path)

save_param_npz(npz, model='gp', neuron_type='proto', store_param_path=store_param_path)
