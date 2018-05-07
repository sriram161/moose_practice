#!/usr/bin/env python3
"""
@Description: Generates modified version of cond_param.py and *.p files based on
               the value in *.npz files.
@Author: Sri Ram Sagar Kappagantula
@Mail: skappag@masonlive.gmu.edu
@Date: 23rd FEB, 2018.
"""

import logging
import fileinput
import shutil
import numpy as np
import re
import sys
from pathlib import Path
from ajustador.helpers.loggingsystem import getlogger

logger = getlogger(__name__)
logger.setLevel(logging.DEBUG)

def load_npz(file_path):
    "Loads the single npz file into environment."
    logger.debug("Path: {}".format(file_path))
    return np.load(file_path)

def create_path(path,*args):
    "Creates sub-directories recursively if they are not available"
    path = Path(path)
    path = path.joinpath(*args) #No data time. add process id from fitobject and row_number for npz.
    logger.debug("Path: {}".format(path))
    if path.exists:
       return path
    path.mkdir(parents=True)
    return path

def get_least_fitness_params(data):
    "Returns least fitness parameters list."
    logger.debug("{}".format(data['fitvals'].shape))
    logger.debug("{}".format(np.argmin(data['fitvals'], axis=0)))
    rows = np.argmin(data['fitvals'], axis=0)
    logger.debug("{}".format(data['fitvals'][np.argmin(data['fitvals'], axis=0)[-1],]))
    return [np.dstack((data['params'][row],data['paramnames'])) for row in rows]

def get_morph_file(line, re_obj, neuron_type):
    "Get morph file name from the the line if the mathes the re_obj."
    if re_obj.match(line):
        logger.debug("Found {}".format(re_obj.match(line).groups()))
        morph_file = re_obj.match(line).group(2) if re_obj.match(line).group(1) == neuron_type else re_obj.match(line).group(4)
        return morph_file
    return None

def process_morph_line(line, re_obj, non_conds):
    if re_obj.match(line):
        logger.debug("Found {} {}".format(re_obj.match(line).groups(), re_obj.match(line).group('feature')))
        if non_conds.get(re_obj.match(line).group('feature'), None):
            new_line=line.replace(re_obj.match(line).group('value'), non_conds.get(re_obj.match(line).group('feature')))
            logger.debug("{}".format(new_line))
            line = new_line
    return line

class State:
    def run(self, line):
        pass

class ModelCompare(State):
    PATTERN = r".*"
    RE_OBJ = re.compile(PATTERN, re.I)
    def run(self, line):
        logger.debug(" Logger in ProtoCompare State!!!")
        match_obj = ProtoCompare.RE_OBJ.match(line)
        if match_obj:
            return(line, 'model', 'feature')
        return(line, 'model', 'write')


class FeatureCompare(State):
    PATTERN = r".*"
    RE_OBJ = re.compile(PATTERN, re.I)
    def run(self, line):
        logger.debug(" Logger in FeatureCompare State!!!")
        match_obj = FeatureCompare.RE_OBJ.match(line)
        if match_obj:
            return(line, 'feature', 'change')
        return(line, 'feature', 'blockend')

class ChangeLine(State):
    PATTERN = r".*"
    RE_OBJ = re.compile(PATTERN, re.I)
    def run(self, line, conds):
        logger.debug(" Logger in ChangeLine State!!!")
        # Modify line and send it to writeout State
        return(new_line, 'changeline', 'write')

class BlockEnd(State):
    PATTERN = r".*"
    RE_OBJ = re.compile(PATTERN, re.I)
    def run(self, line):
        atch_obj = BlockEnd.RE_OBJ.match(line)
        if match_obj:
            return(line, 'blockend', 'writeall')
        return(line, 'blockend', 'write')

class WriteOuput(State):
    def run(self, line):
        logger.debug(" Logger in Write State!!!")
        sys.stdout.write(line)
        return(line, 'write', 'feature')

class WriteAll(State):
    def run(self, line):
        logger.debug("Logger in WriteAll state!!!")
        sys.stdout.write(line)
        return(line, 'writeall', 'writeall')


class CondParamMachine(object):
    machine = None
    def __init__(self, line, initial_state, **all_states):
        if CondParamMachine.machine == None:
            self.all_states = all_states
            self.current_state = initial_state
            self.line, self.prev, self.next = self.current_state.run(line)
            CondParamMachine.machine = self

    def run(self, line):
        self.current_state = self.all_states.get(self.next)
        if self.next == 'write' and self.prev == 'arky':
            # if prev_state is arky return to proto state
            self.line, slef.prev, self.next = self.current_state.run(line)
            self.next == 'proto'
        else:
            self.line, slef.prev, self.next = self.current_state.run(line)




if __name__ == '__main__':
   links = """/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitFgp-proto-proto144.npz
/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitgp-arky-arky120F.npz
/home/ram/neural_prj/prof_resources/parameters_fit_to_param_cond/fitgp-arky-arky140F.npz
"""
   links = links.split('\n')
   neuron_types = [link.rpartition('/')[2].split('-')[1] for link in links if link is not '']
   logger.debug("{}".format(neuron_types))
   store_param_path = "/home/ram/neural_prj/outputs/parameters_sets"
   model = 'gp'
   neuron_type = neuron_types[0]
   morph_file = 'None'
   cond_file = 'param_cond.py'
   moose_nerp_path = "/home/ram/neural_prj/moose_nerp/moose_nerp/"

   pattern_morph = r"^\*set_compt_param\s*(?P<feature>[A-Z]+)\s+(?P<value>[\-.0-9]+)"
   pattern_cond_morph_file =r"morph_file\s+=\s+\{'(proto)'\s*:\s*'([A-Z0-9.a-z_]+)'\s*,\s*'(arky)'\s*:\s*'([A-Z0-9.a-z_]+)'\}"   #need to fix it to make it more generic here I included proto and arky.
   pattern_cond = ""


   morph_cond_re_obj = re.compile(pattern_cond_morph_file, re.I)
   morph_set_re_obj = re.compile(pattern_morph, re.I)

   model_path = Path(moose_nerp_path)/model

   logger.info("START STEP 1!!!loading npz file.")
   data = load_npz(links[0])
   logger.info("END STEP 1!!! loading npz file.")

   logger.info("START STEP 2!!! Prepare params for loaded npz.")
   param_data_list = get_least_fitness_params(data)
   logger.debug("{}".format(param_data_list))
   conds = [(ele[1].split('_')[-2], ele[1].split('_')[-1], ele[0]) for item in param_data_list[-1] for ele in item if '_' in ele[1]]
   logger.debug("{}".format(conds))
   non_conds = [(ele[1].split('_')[-1].upper(), ele[0]) for item in param_data_list[-1] for ele in item if '_' not in ele[1]]
   non_conds = dict(non_conds)
   logger.debug("{}".format(non_conds))
   logger.info("END STEP 2!!! Prepared params for loaded npz.")

   logger.info("START STEP 3!!! Copy file from respective prototye folder to new_param holding folder.")
   new_param_path = create_path(store_param_path, model, neuron_type)
   shutil.copy(model_path/cond_file, new_param_path)
   logger.info("END STEP 3!!! Copy file from respective prototye folder to new_param holding folder.")

   logger.info("START STEP 4!!! Extract morph_file from param_cond.py file in the holding folder")
   with fileinput.input(files=(str(new_param_path/cond_file))) as f_obj:
       for line in f_obj:
           morph_file = get_morph_file(line, morph_cond_re_obj, neuron_type)
           if morph_file is not None:
               break
   logger.debug("morph_file: {}".format(morph_file))
   logger.info("END STEP 4!!! Extract the respective param_cond.py file in the holding folder")

   logger.info("START STEP 5!!! Modify the respective *.p file in the holding folder")
   shutil.copy(model_path/morph_file, new_param_path)
   with fileinput.input(files=(str(new_param_path/morph_file)), inplace=True) as f_obj:
       for line in f_obj:
           new_line = process_morph_line(line, morph_set_re_obj, non_conds)
           sys.stdout.write(new_line)
   logger.info("END STEP 5!!! Modify the respective *.p file in the holding folder")

   logger.info("START STEP 6!!! Modify the respective cond_param.py file in the holding folder.")
   with fileinput.input(files=(str(new_param_path/cond_file)), inplace=True) as f_obj:
       for line in f_obj:
           new_line = process_cond_line(line, morph_set_re_obj, conds) #StateMachine program here
   logger.info("END STEP 6!!! Modify the respective cond_param.py file in the holding folder.")
   logger.info("STEP 7!!! Process complete")
