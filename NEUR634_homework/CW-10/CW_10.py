import moose

synchan = moose.NMDAChan('/cell2/dend/nmda')
synchna.KMg_A = 0.17
synchan.KMg_b = 0.012
synchan.CMg = 1.4

def magnesium_term(A, B, C):
    eta = 1.0/A
    gamma = 1.0/B
    V = np.linspace(-100E-3, )
    mg_term = 1/ ( 1 + eta*C *)

synparams = {}
mgparams = {'A': (1/6.0), 'B':(1/80.0), 'conc': 1.4}
synparams['ampa'] = {'Erev': 5E-3, 'tau1': 1.0E-3, 'tau2': 5E-3, 'Gbar': 1E-9}
synparams['nmda'] = {'Erev': 5E-3, 'tau1': 1.1E-3, 'tau2': 37.5E-3, 'Gbar': 2E-9, 'mgparams': mgparams}

from pprint import pprint
pprint(synparams, width=40)

for key, params in synparams.items():
    if key == 'nmda':
        chan = moose.NMDAChan('/cell2/dend/' + key)
        chan.KMg_A = params['mgparams']['A']
        chan.KMg_B = params['mgparams']['B']
        chan.CMg = params['mgparams']['conc']
    else:
        chan = moose.SynChan('/cell2/dend/' + key)
        chan.Gbar = params['Gbar']
        chan.tau1 = params['tau1']
        chan.tau2 = params['tau2']
        chan.Ek = params['Erev']

# Test to check NMDA creation.
moose.le('/cell2/dend')

for key, params in synparams.items():
    if key == 'nmda':
        chan = moose.NMDAChan('/cell2/dend/' + key)
        chan.KMg_A = params['mgparams']['A']
        chan.KMg_B = params['mgparams']['B']
        chan.CMg = params['mgparams']['conc']
        chan.temperature = params['temperature']
        chan.extCa = params['extCa']
        chan.condFraction = params['condFraction']
    else:
        chan = moose.SynChan('/cell2/dend/' + key)
        chan.Gbar = params['Gbar']
        chan.tau1 = params['tau1']
        chan.tau2 = params['tau2']
        chan.Ek = params['Erev']

m = moose.connect(nmdachan, 'ICaOut', capool, 'current')

capool = moose.CaConc('/cell2/dend/capool')
moose.showfield(capool)

m = moose.connect(capool, 'concOut', nmdachan, 'setIntCa')

moose.showmsg('/cell2')
