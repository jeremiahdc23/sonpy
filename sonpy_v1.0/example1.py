# -*- coding: utf-8 -*-

import sonpy
import os

# This is a very simple example of the usage of SonPy, where we rely on
# runMakeover() to set the layer properties.

if __name__ == '__main__':

    # Create an instance of Sonnet
    snt = sonpy.sonnet()

    # Set where your Sonnet installation bin folder is
    snt.setSonnetInstallationPath('C:\\Program Files (x86)\\Sonnet Software\\16.54\\bin')

    # Set the gds file with our circuit design
    snt.setGdsFilePath(os.getcwd())
    snt.setGdsFile('example.gds')

    # Run a predefined set of commands that imports the gds file and sets the
    # bottom dielectric layer to silicon with a chip of lossless metal. It is
    # assumed that the gds layers have the numbers 23 (single metal layer) or
    # 23, 50 and 51 (chip with air bridges). Please look at runMakeover() in
    # sonpy.py for more details about the commands this function runs.
    snt.runMakeover()

    # Add ports to the circuit
    snt.addPort(0, 216)
    snt.addPort(225, 580)
    snt.addPort(505, 292)
    snt.addPort(390, 0)
    snt.addPort(60, 0)

    # Add lumped elements ("components") such as an inductor
    snt.addComponent(236.5, 180, 272.5, 180, xmargin=2, ymargin=2, tlayer_index=23, component_type="ind", value=14)

    # Print the layer configuration, ports and components to the consol to verify our changes
    snt.printLayers()

    # The runMakeover() function has set a default frequency sweep and output
    # file format, but we can change that if we wish.

    # Set an adaptive frequency sweep from 4 GHz to 6 GHz
    snt.setFrequencySweep(f1=4, f2=6)

    # Save the S parameters in dB to example.csv
    snt.setOutput(filename="example.csv", partype="S", parform="DB")

    # When we are done with configuring our project, we run the simulation
    snt.runSimulationStatusMonitor()
