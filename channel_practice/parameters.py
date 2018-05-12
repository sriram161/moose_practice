from collections import namedtuple

Chn_param = namedtuple("params", "A_A A_B A_C A_D A_F B_A B_B B_C B_D B_F")
Voltage_scale = namedtuple("Voltage_scale", "VDIVS VMIN VMAX")

EREST_ACT = -70e-3

def get_voltage_scales():
    global EREST_ACT
    VMIN = -30e-3 + EREST_ACT
    VMAX = 120e-3 + EREST_ACT
    VDIVS = 3000
    return Voltage_scale(VDIVS, VMIN, VMAX)

def get_na_m_params(VSHIFT=0, tau=1, f=0):
  global EREST_ACT
  return Chn_param(
  A_A = -1e5 * (-25e-3 - EREST_ACT - VSHIFT)*tau,
  A_B = -1e5*tau,
  A_C = -1.0,
  A_D = -25e-3 - EREST_ACT - VSHIFT,
  A_F = -10e-3 + f,

  B_A = 4e3*tau,
  B_B = 0.0*tau,
  B_C = 0.0,
  B_D = 0.0 - EREST_ACT - VSHIFT,
  B_F = 18e-3 + f)

def get_na_h_params(VSHIFT=0, tau=1, f=0):
  global EREST_ACT
  return Chn_param(
  A_A = 70.0*tau,
  A_B = 0.0*tau,
  A_C = 0.0,
  A_D = 0.0 - EREST_ACT - VSHIFT,
  A_F = 0.02 + f,

  B_A = 1000.0*tau,
  B_B = 0.0*tau,
  B_C = 1.0,
  B_D = -30e-3 - EREST_ACT - VSHIFT,
  B_F =  -0.01 + f)

def get_k_n_params(VSHIFT=0, tau=1, f=0):
  global EREST_ACT
  return Chn_param(
  A_A = -1e4 * (-10e-3 - EREST_ACT - VSHIFT)*tau,
  A_B = -1e4*tau,
  A_C = -1.0,
  A_D = -10e-3 - EREST_ACT - VSHIFT,
  A_F = -10e-3 + f,

  B_A = 0.125e3*tau,
  B_B = 0.0*tau,
  B_C = 0.0,
  B_D = 0.0 - EREST_ACT - VSHIFT,
  B_F = 80e-3 + f)

# cell_proto.py in moose_nerp
