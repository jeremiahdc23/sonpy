# -*- coding: utf-8 -*-

import sonpy
import time

snt = sonpy.sonnet()

snt.setGdsFilePath('C:\\Users\\...\\myfolder\\')
snt.setGdsFile('myfile.gds')

# Convert gds file to Sonnet project file and set the dielectric
# properties to a bottom of silicon with vacuum above
# (work with zero or one air bridge)
snt.runMakeover()

# Print an overview of the layers
snt.printLayers()

# Add ports
snt.addPort(x1, y1) # port 1
snt.addPort(x2, y2) # port 2

# Add components (here a 40 nH inductor in dielectric layer 1)
snt.addComponent(x1, y1, x2, y2, dielectriclayer=1, type="ind", value=40) # L1
# Note: Inductors are automatically labelled L1, L2,...

# Add a frequency sweep from f1 to f2 in steps of fstep (in GHz)
snt.setFrequencySweep(f1, f2, fstep)
# Note: If fstep is not given, Sonnet will run an adaptive sweep

# We can also sweep over a parameter, say the inductor defined before
snt.setParameterSweep("L1", pmin, pmax, pstep)
# Note: pmin, pmax and pstep is in nH because we sweep an inductor
# Note: Because we defined a frequency sweep before, Sonnet will sweep
#       over those frequencies while sweeping L1. We can also redefine
#       the frequency sweep by giving setParameterSweep the optional
#       arguments f1, f2 and fstep (with same effect as above)

# Run the simulation
snt.runSimulation()
