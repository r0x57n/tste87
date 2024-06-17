# -*- coding: utf-8 -*-
from b_asic.core_operations import Addition, ConstantMultiplication
from b_asic.signal_flow_graph import SFG
from b_asic.special_operations import Delay, Input, Output
from b_asic.sfg_generators import wdf_allpass
from b_asic.simulation import Simulation
import numpy as np
import matplotlib.pyplot as plt
from b_asic.signal_generator import Impulse
from mplsignal.freq_plots import freqz_fir

#%%
# a) Create an SFG for the filter

a0 = 167/256
a1 = -135/256
a2 = 1663/2048
a3 = -1493/2048
a4 = 669/1024
a5 = -117/128
a6 = 583/1024

x = Input()
x.graph_id = "x(n)"

allpass_upper = wdf_allpass([a0, a3, a4]) 
allpass_lower = wdf_allpass([a1, a2, a5, a6])

allpass_upper <<= x
allpass_lower <<= x

add0 = allpass_upper + allpass_lower
add0.graph_id = "+"
c0 = ConstantMultiplication(0.5, add0)
c0.graph_id = "1/2"
y = Output(c0)
y.graph_id = "y(n)"

allpass_upper.connect_external_signals_to_components()
allpass_lower.connect_external_signals_to_components()

sfg = SFG([x], [y])
sfg

#%%
# b) Simulate the filter using an impulse and check the values of all interesting nodes. Comments?
sim = Simulation(sfg, [Impulse()])
sim.run_for(100)

print(np.sqrt(sum(abs(sim.results["sym2p0.0"])**2)))
print(np.sqrt(sum(abs(sim.results["sym2p1.0"])**2)))
print(np.sqrt(sum(abs(sim.results["sym2p2.0"])**2)))
print(np.sqrt(sum(abs(sim.results["sym2p3.0"])**2)))
print(np.sqrt(sum(abs(sim.results["sym2p5.0"])**2)))
print(np.sqrt(sum(abs(sim.results["sym2p7.0"])**2)))
print(np.sqrt(sum(abs(sim.results["sym2p9.0"])**2)))

#%%
# c) Plot the phase-response of the two allpass branches in the same plot. 
allpass_upper = wdf_allpass([a0, a3, a4]) 
allpass_lower = wdf_allpass([a1, a2, a5, a6])

sim_upper = Simulation(allpass_upper, [Impulse()])
sim_upper.run_for(100)
sim_lower = Simulation(allpass_lower, [Impulse()])
sim_lower.run_for(100)

freqz_fir(sim_upper.results["0"], whole=True)
fig = freqz_fir(sim_lower.results["0"], whole=True)

#%%
# d) How large is the difference in phase in the pass- and stopband? 
# Difference in phase (guess of where, how to see?),  
# Passband: ~Pi  
# Stopband: ~2*Pi

#%%
# e) Scale the filter using L2-scaling
# Critical: sym2p2 (a4), sym2p7 (a6), sym2p9 (a3)

new_x = Input()

new_allpass_upper = wdf_allpass([a0, a3, a4]) 
new_allpass_lower = wdf_allpass([a1, a2, a5, a6])

new_c1 = ConstantMultiplication(2**(-3), new_x)
new_c2 = ConstantMultiplication(2**3, new_allpass_lower)

new_c3 = ConstantMultiplication(2**(-2), new_x)
new_c4 = ConstantMultiplication(2**2, new_allpass_upper)

new_allpass_upper <<= new_c3
new_allpass_lower <<= new_c1

new_add0 = new_c4 + new_c2
new_c0 = ConstantMultiplication(0.5, new_add0)
new_y = Output(new_c0)

new_allpass_upper.connect_external_signals_to_components()
new_allpass_lower.connect_external_signals_to_components()

new_sfg = SFG([new_x], [new_y])
new_sfg

#%%
# f) Simulate the scaled filter.
#    What is the value of the L2-sum in the different nodes? 
#    Are the nodes correctly scaled?
#    How can you verify that the filter function is not changed? 
new_sim = Simulation(new_sfg, [Impulse()])
new_sim.run_for(100)

print(np.sqrt(sum(abs(new_sim.results["sym2p0.0"])**2)))
print(np.sqrt(sum(abs(new_sim.results["sym2p1.0"])**2)))
print(np.sqrt(sum(abs(new_sim.results["sym2p2.0"])**2)))
print(np.sqrt(sum(abs(new_sim.results["sym2p3.0"])**2)))
print(np.sqrt(sum(abs(new_sim.results["sym2p6.0"])**2)))
print(np.sqrt(sum(abs(new_sim.results["sym2p4.0"])**2)))
print(np.sqrt(sum(abs(new_sim.results["sym2p8.0"])**2)))

fig, ax = plt.subplots()
ax.stem(sim.results["0"],markerfmt="*")
ax.stem(new_sim.results["0"],markerfmt="x")

#%%
# g) Simulate the scaled filter with a random input.
#    Comments?
#    Can overflow occur in any node?  YES
data = np.random.rand(100)*2 - 1
rand_sim = Simulation(new_sfg, [data])
rand_sim.run_for(100)

fig, ax = plt.subplots()
ax.stem(rand_sim.results["0"])

#%%
# h) Introduce a pipelining delay in each branch and compare the output with
#    the non-pipelined SFG.
#    Comments? 
pipelined_sfg = sfg.insert_operation_after("x(n)", Delay())
pipelined_sfg
pipelined_sim = Simulation(pipelined_sfg, [data])
pipelined_sim.run_for(100)

fig, ax = plt.subplots()
ax.stem(rand_sim.results["0"], markerfmt="X")
ax.stem(pipelined_sim.results["0"], markerfmt="*")

#%%
# i) Plot the precedence graph for the pipelined SFG. 
pipelined_sfg.precedence_graph
