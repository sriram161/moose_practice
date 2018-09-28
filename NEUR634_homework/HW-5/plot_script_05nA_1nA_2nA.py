import matplotlib.pyplot as plt
import numpy as np

file1 = 'sim_05nA.npy'
file2 = 'sim_1nA.npy'
file3 = 'sim_2nA.npy'

simtime = 0.1
data1 = np.load(file1)
data2 = np.load(file2)
data3 = np.load(file3)
t = np.linspace(0, simtime, len(data1))

plt.plot(t, data1, t, data2, t, data3)
plt.title('Compare simulations with varied injection currents')
plt.legend(['0.5nA', '1nA', '2nA'])
plt.grid(True)
plt.show()
