# -*- coding: utf-8 -*-

import sonpy
import os
import matplotlib as plt

# This is an example of the usage of SonPy where we set the layer properties
# manually (i.e. not through runMakeover()). Furthermore, we create a lumped
# element inductor of variable inductance which we sweep in the simulation.

if __name__ == '__main__':

    # Create an instance of Sonnet
    snt = sonpy.sonnet()

    # Set where your Sonnet installation bin folder is
    snt.setSonnetInstallationPath('C:\\Program Files (x86)\\Sonnet Software\\16.54\\bin')

    # Set the gds file with our circuit design
    snt.setGdsFilePath(os.getcwd())
    snt.setGdsFile('example.gds')

    # Import the gds file
    snt.runGdsTranslator()

    # Set up the dielectric layer properties and stackup
    snt.setDlayer(dlayer_index=1, thickness=279, erel=11.45, eloss=1e-6, name="Silicon")
    snt.setDlayer(dlayer_index=0, thickness=2.9, erel=1, eloss=0, name="Vacuum")
    snt.addDlayer(thickness=500, erel=1, eloss=0, name="Vacuum")

    # Set the technology layer properties (circuit and air bridges)
    snt.setTlayer(tlayer_index=23, dlayer_index=1, lossless=True)
    snt.setTlayer(tlayer_index=50, dlayer_index=0, lossless=True)
    snt.setTlayer(tlayer_index=51, lay_type="via", dlayer_index=1, to_dlayer_index=0, lossless=True)

    # Add ports to the circuit
    snt.addPort(0, 216)
    snt.addPort(225, 580)
    snt.addPort(505, 292)
    snt.addPort(390, 0)
    snt.addPort(60, 0)

    # Create a variable inductance "L"
    snt.addParameter("L", "ind")

    # Add lumped element inductor with the inductance "L"
    snt.addComponent(236.5, 180, 272.5, 180, xmargin=2, ymargin=2, tlayer_index=23, component_type="ind", value="L")

    # Sweep the inductance "L" from 10 nH to 15 nH in steps of 1 nH,
    # and sweep the frequency adaptively from 4 GHz to 6 GHz
    snt.addParameterSweep("L", pmin=10, pmax=15, pstep=1, f1=4, f2=6)

    # Print the layer configuration, ports and components to the consol to verify our changes
    snt.printLayers()

    # Print the variables to verify that we have set up our sweeps correctly
    snt.printParameters()

    # Save the S parameters in dB to example.csv
    snt.setOutput(filename="example.csv", partype="S", parform="DB")

    # When we are done with configuring our project, we run the simulation
    snt.runSimulationStatusMonitor()

    # When the output is created, we can extract some data and plot it.
    # Let us plot frequency vs. S45 for the first run of the parameter "L"
    xdata = snt.getOutput(data="frequency", run=1)
    ydata = snt.getOutput(data="DB[S45]", run=1)
    plt.plot(xdata, ydata)
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("S45 [dB]")
    plt.show()
