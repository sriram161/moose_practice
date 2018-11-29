import moose

def chirp(gen_name="chirp", f0=1, f1=50, T=0.8, start=0.1, end=0.5, simdt=10E-5):
    func_1 = moose.Func("/"+gen_name)
    func_1.mode = 3
    func_1.expr = 'cos(2*pi*({f1}-{f0})/{T}*x^2 + 2*pi*{f1}*x)'.format(f0=f0, f1=f1, T=T)
    input = moose.StimulusTable('/xtab')
    xarr = np.arange(start, end, simdt)
    input.vector = xarr
    input.startTime = 0.0
    input.stepPosition = xarr[0]
    input.stopTime = xarr[-1] - xarr[0]
    moose.connect(input, 'output', func_1, 'xIn')
    return func_1

chirp_test = chirp()
tab = moose.Table('/check')
moose.connect(tab, 'requestOut', chirp_test, 'getValue')
moose.reinit()
moose.start(1)

import matplotlib.pyplot as plt
plt.plot(tab.vector)
plt.show()
