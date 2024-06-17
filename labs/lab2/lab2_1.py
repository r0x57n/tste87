# -*- coding: utf-8 -*-
from b_asic.core_operations import Addition, ConstantMultiplication
from b_asic.signal_flow_graph import SFG
from b_asic.special_operations import Delay, Input, Output
from b_asic.sfg_generators import wdf_allpass

#%%
# a) Simulate the impulse response for the complete interpolator filter.

a1 = -0.068129
a3 = -0.242429
a5 = -0.461024
a7 = -0.678715
a9 = -0.888980

a10 = 0.4573
a11 = -0.2098
a12 = 0.5695
a13 = -0.2123
a14 = 0.0952
a15 = -0.2258
a16 = -0.4490

x = Input()
x.graph_id = "x(n)"

# Create all WDFes
wdf_up1 = wdf_allpass([a3])
wdf_up2 = wdf_allpass([a7])
wdf_down1 = wdf_allpass([a1])
wdf_down2 = wdf_allpass([a5])
wdf_down3 = wdf_allpass([a9])

# Misc
v0 = Delay(x)

# Create the delays used after each WD
v1 = Delay()
v1.graph_id = "v1"
v3 = Delay()
v3.graph_id = "v3"
v5 = Delay()
v5.graph_id = "v5"
v7 = Delay()
v7.graph_id = "v7"
v9 = Delay()
v9.graph_id = "v9"

# Create multiplications used after each WD
c1 = ConstantMultiplication(-1)
c1.graph_id = "c1"
c2 = ConstantMultiplication(-1)
c2.graph_id = "c2"
c3 = ConstantMultiplication(-1)
c3.graph_id = "c3"
c4 = ConstantMultiplication(-1)
c4.graph_id = "c4"
c5 = ConstantMultiplication(-1)
c5.graph_id = "c5"

# Connect the WDFs with input/eachother
wdf_up1 <<= v0
wdf_up2 <<= wdf_up1
wdf_down1 <<= x
wdf_down2 <<= wdf_down1
wdf_down3 <<= wdf_down2

# The output part
add0 = wdf_up2 - wdf_down3
c0 = ConstantMultiplication(0.5, add0)
y = Output(c0)

# Graph IDs for easier debugging
v0.graph_id = "v0"
add0.graph_id = "+"
c0.graph_id = "1/2"
y.graph_id = "y(n)"

# Connect everything for initial SFG
wdf_up1.connect_external_signals_to_components()
wdf_up2.connect_external_signals_to_components()
wdf_down1.connect_external_signals_to_components()
wdf_down2.connect_external_signals_to_components()
wdf_down3.connect_external_signals_to_components()
sfg = SFG([x], [y])

# Connect the delays/multiplications after each WDF
sfg = sfg.insert_operation_after("sym2p0.1", c1)
sfg = sfg.insert_operation_after("c1", v1)
sfg = sfg.insert_operation_after("sym2p2.1", c2)
sfg = sfg.insert_operation_after("c2", v3)
sfg = sfg.insert_operation_after("sym2p8.1", c3)
sfg = sfg.insert_operation_after("c3", v5)
sfg = sfg.insert_operation_after("sym2p6.1", c4)
sfg = sfg.insert_operation_after("c4", v7)
sfg = sfg.insert_operation_after("sym2p4.1", c5)
sfg = sfg.insert_operation_after("c5", v9)

sfg