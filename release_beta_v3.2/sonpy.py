# -*- coding: utf-8 -*-

import subprocess
import time
import os
#import gdspy # only needed for getGdsLayers (not used)
from win32com.client import GetObject # outcomment only on Linux!

# PROGRAM:     SonPy
# VERSION:     $\beta$ 3.2 (June 5, 2018)
# PURPOSE:     Python interface for Sonnet.
# LICENSE:     GNU General Public License 3.0
# AUTHOR:      Niels Jakob Søe Loft
# DEVELOPMENT: Daniel Becerra, Bharath Kannan

# CHANGES SINCE LAST VERSION:
# New function: getOutput for data extraction
# Changed function: addPort now searches for nearby attachment edges
# Changed function: getLayers, now using dicts for ports, layers and components

class _layer():
    # Each instance of the class _layer is a single dielectric layer including
    # a list of any technology layers, ports or components in the layer.
    # All of these object (dielectric layers, technology layers, ports and
    # components) are dictionaries with the relevant parameters, see
    # the getLayers() function which is the one creating layer classes.

    def __init__(self, dlayer):
        self._dielectric_layer = dlayer
        self._technology_layers = []
        self._ports = []
        self._components = []

    def recordTechnologyLayer(self, tlayer):
        self._technology_layers.append(tlayer)

    def recordPort(self, port):
        self._ports.append(port)

    def recordComponent(self, component):
        self._components.append(component)


class sonnet(object):
   # Class for interactions between Sonnet and Python
   # Tested on Windows, can be extended to Linux (but not Mac)

    def __init__(self):
        # Settings for em simulator
        self._exception = Exception
        self._executable_path = "C:\\Program Files (x86)\\Sonnet Software\\14.54\\bin\\"
        self._executable_file = "em.exe"
        self._executable_and_monitor_file = "emstatus.exe"
        self._executable_and_monitor_options = "-Run"
        self._sonnet_file_path = "C:\\Users\\Lab\\Desktop\\sonnet_test\\"
        self._sonnet_file = "test.son"
        self._sonnet_options = "-v"
        self._done_flag = 1
        self._run_count = 0
        self._output = None
        self._em_process = None
        self._emstatus_process = None
        self._parentPID = None
        self._emPID = None
        self._winprocessParent = None

        # Settings for .gds to .son translator
        self._gds_translator_file = "gds.exe"
        self._gds_translator_options = "-v"
        self._gds_file_path = self._sonnet_file_path
        self._gds_file = "test.gds"
        self._gds_process = None

        # Settings for data extraction and plotting
        self._data_file = self._sonnet_file[:-4] + ".csv"
        self._data_file_path = self._sonnet_file_path

    def __del__(self):
        self._em_process = None
        self._emstatus_process = None

    ########################################################################
    # SONNET SIMULATOR (em.exe and emstatus.exe)                           #
    ########################################################################

    def setSonnetFile(self, filename):
        self._sonnet_file = filename

    def setSonnetFilePath(self, path):
        self._sonnet_file_path = path

    def setSonnetInstallationPath(self, path):
        self._executable_path = path

    def runSimulation(self):
        if (self._done_flag == 0):
            print("Can't start new simulation until previous simulation completes, please run checkDone() to see if previous simulation completed")
            return

        # Verify Sonnet project file exists
        file_found = 0
        for root, dirs, files in os.walk(self._sonnet_file_path):
            for file in files:
                # Make search case insensitive
                if self._sonnet_file.lower() == file.lower():
                    file_found = 1

        if (file_found == 0):
            print("Project file %s can not be located in path %s"%(self._sonnet_file,self._sonnet_file_path))
            raise self._exception("Sonnet project file not found! Check that directory and filename are correct!")

        self._done_flag = 0
        args = ([self._executable_path+self._executable_file, # command
                 self._sonnet_options, # options
                 self._sonnet_file_path+self._sonnet_file]) # file

        try:
            self._em_process = subprocess.Popen(args, stdout=subprocess.PIPE)
            self._run_count = self._run_count + 1
            self._output = None
        except:
            print("Error! Can't start process, use setSonnetInstallationPath(path) to point the class to the location of your em.exe file")
            print("Current path is %s"%self._executable_path)
            self._done_flag = 1
            raise self._exception("Can not run sonnet executable file, file not found")

    def checkDone(self):
        if (self._em_process.poll() == 0):
            print("Done succesfully!")
            self._done_flag = 1
            return 0
        else:
            WMI = GetObject('winmgmts:')
            processes = WMI.InstancesOf('Win32_Process')
            winprocesses=[process.Properties_('ProcessId').Value for process in processes]
            try:
                processfound=winprocesses.index(self._em_process.pid)
                print("Process (PID: %d) alive! Simulation still running!"%self._em_process.pid)
                return 1
            except:
                print("Process (PID: %d) dead, possible error (sonnet licence limitation?) Simulation failed!"%self._em_process.pid)
                self._done_flag = 1
                self._output = None
                return -1

    '''
    def getOutput(self, visible=0):
        if ( (self._done_flag == 1) and (self._run_count > 0) ):
            if (self._output == None):
                self._output = self._em_process.stdout.readlines()
                if (visible==1):
                    for element in self._output:
                        print(element)
            else:
                print("Output from previous run still in buffer")
        else:
            print("Simulation is not done!")
    '''

    def runSimulationStatusMonitor(self):
        if (self._done_flag == 0):
            print("Can't start new simulation until previous simulation completes, please run checkDoneSimAndStatus() to see if previous simulation completed")
            return

        # Verify Sonnet project file exists
        file_found = 0
        for root, dirs, files in os.walk(self._sonnet_file_path):
            for file in files:
                # Make search case insensitive
                if self._sonnet_file.lower() == file.lower():
                    file_found = 1

        if (file_found == 0):
            raise self._exception("Sonnet project file %s can not be located in path %s"%(self._sonnet_file,self._sonnet_file_path))

        self._done_flag = 0
        args = ([self._executable_path+self._executable_and_monitor_file, # command
              self._executable_and_monitor_options, # options
              self._sonnet_file_path+self._sonnet_file]) # file
        try:
            self._emstatus_process = subprocess.Popen(args, stdout=subprocess.PIPE)
            self._run_count = self._run_count + 1
            self._output = None
        except:
            print("Error! Can't start process, use setSonnetInstallationPath(path) to point the class to the location of your em.exe file")
            print("Current path is %s"%self._executable_path)
            self._done_flag = 1
            raise self._exception("Can not run sonnet executable file, file not found")
        time.sleep(5)
        self.getEmProcessID()

    def getEmProcessID(self):
        # Based on SimulationStatusMonitor process 'emstatus.exe', find out child process 'em.exe'
        WMI = GetObject('winmgmts:')
        processes = WMI.InstancesOf('Win32_Process')
        self._parentPID = int(self._emstatus_process.pid)
        self._emPID = None
        for process in processes:
            parent = int(process.Properties_('ParentProcessId').Value)
            child = int(process.Properties_('ProcessId').Value)
            if (parent == self._parentPID):
                self._emPID = child
                break

    def checkDoneSimAndStatus(self):
        if (self._emPID):
            WMI = GetObject('winmgmts:')
            processes = WMI.InstancesOf('Win32_Process')
            winprocesses=[int(process.Properties_('ProcessId').Value) for process in processes]
            if (self._emPID in winprocesses):
                print("Process (PID: %d) alive! Simulation still running! Parent PID %d"%(self._emPID, self._parentPID))
                return 1
            else:
                self._done_flag = 1
                for process in processes:
                    if (process.Properties_('ProcessId').Value == self._parentPID):
                        str_methods = process.Methods_('Terminate')
                        str_params=str_methods.InParameters
                        str_params.Properties_('Reason').Value=0
                        process.ExecMethod_('Terminate',str_params)
                        return 0
        else:
            self._done_flag = 1
            print("Simulation did not run")
            return -1

    ########################################################################
    # GDS TO SON TRANSLATOR (gds.exe)                                      #
    ########################################################################

    def setGdsFile(self, filename):
        self._gds_file = filename

    def setGdsFilePath(self, path):
        self._gds_file_path = path

    def runGdsTranslator(self):
        # Verify gds file exists
        file_found = 0
        for root, dirs, files in os.walk(self._gds_file_path):
            for file in files:
                # Make search case insensitive
                if self._gds_file.lower() == file.lower():
                    file_found = 1

        if (file_found == 0):
            print("GDSII file %s cannot be located in path %s"%(self._gds_file,self._gds_file_path))
            raise self._exception("GDSII file not found! Check that directory and filename are correct")

        # Convert gds file to son file through Sonnet's gds.exe
        args = ([self._executable_path+self._gds_translator_file, # command
                 self._gds_translator_options, # options
                 self._gds_file_path+self._gds_file]) # file

        try:
            # Run conversion process
            self._gds_process = subprocess.Popen(args, stdout=subprocess.PIPE)

        except:
            print("Error! Cannot start process, use setSonnetInstallationPath(path) to point the class to the location of your gds.exe file")
            print("Current path is %s"%self._executable_path)
            raise self._exception("Cannot run gds executable file, file not found")

        # Wait for the process to complete
        self._gds_process.wait()

    '''
    ## The function works (requires import gdspy), but is not necessary
    def getGdsLayers(self):
        # Returns a list of gds_stream integers used for layers in the gds file
        # These numbers are used to index the technology layers

        # Verify gds file exists
        file_found = 0
        for root, dirs, files in os.walk(self._gds_file_path):
            for file in files:
                # Make search case insensitive
                if self._gds_file.lower() == file.lower():
                    file_found = 1

        if (file_found == 0):
            print("GDSII file %s cannot be located in path %s"%(self._gds_file,self._gds_file_path))
            raise self._exception("GDSII file not found! Check that directory and filename are correct")

        # Get the layers in the gds file
        gdsfile = gdspy.GdsLibrary(infile = self._gds_file_path + self._gds_file)
        layers = []
        for k, v in gdsfile.cell_dict.items():
            for layer in list(v.get_layers()):
                layers.append(layer)

        return layers
    '''

    ########################################################################
    # PORTS AND COMPONENTS                                                 #
    ########################################################################
    # Standard ports: POR1 in the GEO block. Only type = STD is supported.
    # Ideal components: SMD in the GEO block. Only ideal components are supported.

    def getNumberOfPorts(self, type="all"):
        # Returns the number of ports of the specified type where type can be
        # "port" (POR1/regular ports), "component" (SMD/components), or "all" (POR1 and SMD)

        numberOfPorts = 0

        if type not in ["all", "port", "component"]:
            raise self._exception("Invalid port type: {:s}".format(type))

        with open(self._sonnet_file_path + self._sonnet_file, 'r') as fd:
            contents = fd.readlines()
            # Find POR1 and SMD definitions
            for index, line in enumerate(contents):
                if line.split()[0] == "SMD" and type in ["all", "component"]:
                    numberOfPorts += 2 # Two ports for each ideal component
                elif line.split()[0] == "POR1" and type in ["all", "port"]:
                    numberOfPorts += 1

        return numberOfPorts

    def shiftPorts(self, xshift, yshift, type="all"):
        # Shifts the positions of all ports of the specified type
        # ("port", "component" or "all") by (xshift, yshift) in LLC system

        # Map the relative coordinates to Sonnet's ULC system
        xshift, yshift = xshift, -yshift

        if type not in ["all", "port", "component"]:
            raise self._exception("Invalid port type: {:s}".format(type))

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            for index, line in enumerate(contents):
                if line.split()[0] == "SMD" and type in ["all", "component"]:
                    # Update SBOX
                    params = contents[index + 4].split()
                    params[1] = "{:f}".format(float(params[1]) + xshift)
                    params[2] = "{:f}".format(float(params[2]) + xshift)
                    params[3] = "{:f}".format(float(params[3]) + yshift)
                    params[4] = "{:f}".format(float(params[4]) + yshift)
                    contents[index + 4] = " ".join(params) + "\n"
                    # Update LPOS
                    params = contents[index + 6].split()
                    params[1] = "{:f}".format(float(params[1]) + xshift)
                    params[2] = "{:f}".format(float(params[2]) + yshift)
                    contents[index + 6] = " ".join(params) + "\n"
                    # Update SMDP1
                    params = contents[index + 8].split()
                    params[2] = "{:f}".format(float(params[2]) + xshift)
                    params[3] = "{:f}".format(float(params[3]) + yshift)
                    contents[index + 8] = " ".join(params) + "\n"
                    # Update SMDP2
                    params = contents[index + 9].split()
                    params[2] = "{:f}".format(float(params[2]) + xshift)
                    params[3] = "{:f}".format(float(params[3]) + yshift)
                    contents[index + 9] = " ".join(params) + "\n"
                elif line == "POR1 STD\n" and type in ["all", "port"]:
                    # Update POR1
                    params = contents[index + 3].split()
                    params[5] = "{:f}".format(float(params[5]) + xshift)
                    params[6] = "{:f}".format(float(params[6]) + yshift)
                    contents[index + 3] = " ".join(params) + "\n"

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def addPort(self, xcoord, ycoord, xmargin=0.005, ymargin=0.005, **kwargs):
        # Add a POR1 STD definition in the GEO block
        # The DIAGALLOWED line is not supported (i.e. not written to file)
        # The default port number is the number of existing ports (including
        # ports in components) + 1.
        # The function looks for attachement points within xcoord ± xmargin
        # in the x direction and ycoord ± ymargin in the y direction. The
        # attachment point closest to (xcoord, ycoord) is picked.
        # For several equally good attachment points the first one is picked.
        # By default we look for atttachment points among all technology
        # layers, but the search range can be decreased by setting the keyword
        # argument technologylayer to a single integer or list of integers
        # with the gds indices of the technology layers.

        # Map coordinates to Sonnets ULC system
        xcoord, ycoord = self.mapPoint(xcoord, ycoord)

        # List all technology layers (default search range)
        layers = self.getLayers()
        tlayers = []
        for layer in layers:
            for tlayer in layer._technology_layers:
                tlayers.append(tlayer["gds_stream"])
        tlayers = list(set(tlayers))

        dictParams = ({"technologylayer": tlayers,
                       "portnum": self.getNumberOfPorts(type="all") + 1,
                       "resist": 50,
                       "react": 0,
                       "induct": 0,
                       "capac": 0})

        # Update parameters with the user's input
        for key in kwargs.keys():
            if key not in dictParams:
                raise self._exception("Invalid argument: {:s}".format(key))
        dictParams.update(kwargs)

        # Make sure the search range is a list of valid technology layers
        if type(dictParams["technologylayer"]) == int:
            dictParams["technologylayer"] = [dictParams["technologylayer"]]
        for input_tlayer in dictParams["technologylayer"]:
            if input_tlayer not in tlayers:
                raise self._exception("Invalid technology layer: {:d}".format(input_tlayer))

        # Create a list of search strings from the search technology layers
        searchStrs = ["TLAYNAM Stream{:d}".format(tlayer) for tlayer in dictParams["technologylayer"]]

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            candidateVertices = []
            for index, line in enumerate(contents):
                if " ".join(line.replace(":"," ").split()[0:2]) in searchStrs:
                    currentIndex = index
                    while len(contents[currentIndex].split()) != 13:
                        currentIndex += -1
                    nvertices = int(contents[currentIndex].split()[1])
                    debugid = int(contents[currentIndex].split()[4])
                    startIndex = index + 1
                    for tmpIndex in range(startIndex, startIndex + nvertices - 1):
                        x0 = float(contents[tmpIndex].split()[0])
                        y0 = float(contents[tmpIndex].split()[1])
                        x1 = float(contents[tmpIndex + 1].split()[0])
                        y1 = float(contents[tmpIndex + 1].split()[1])
                        # If the attachment point is close enough to the polygon edge,
                        # we save the vertex index (ivertex), polygon index (ipolygon)
                        # and a (simplified) distance error
                        if min(x0,x1) - xmargin <= xcoord and \
                           xcoord <= max(x0,x1) + xmargin and \
                           min(y0,y1) - ymargin <= ycoord and \
                           ycoord <= max(y0,y1) + ymargin:
                            if x0 == x1:
                                error = (xcoord - x0)**2
                                candidateVertices.append([debugid, tmpIndex - startIndex, error])
                            elif y0 == y1:
                                error = (ycoord - y0)**2
                                candidateVertices.append([debugid, tmpIndex - startIndex, error])
                            else:
                                error = ycoord - y0 - (y1 - y0)/(x1 - x0)*(xcoord - x0)**2 \
                                      + xcoord - x0 - (x1 - x0)/(y1 - y0)*(ycoord - y0)**2
                                candidateVertices.append([debugid, tmpIndex - startIndex, error])

            # Evalute the found potential polygon edges to attach to
            if len(candidateVertices) == 0:
                raise self._exception("No polygon edges found to attach port to!")
            # Sort according to error and add the best to dictParams
            candidateVertices.sort(key=lambda item: item[2])
            dictParams.update({"ipolygon": candidateVertices[0][0],
                               "ivertex": candidateVertices[0][1]})

            # Write POR1 definition to son file
            for index, line in enumerate(contents):
                if line.split()[0] == "NUM":
                    contents.insert(index, "POR1 STD\n")
                    contents.insert(index + 1, "POLY {ipolygon} 1\n".format(**dictParams))
                    contents.insert(index + 2, "{ivertex}\n".format(**dictParams))
                    contents.insert(index + 3, "{portnum} {resist} {react} {induct} {capac} {:s} {:s}\n".format(str(xcoord), str(ycoord), **dictParams))
                    break

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def setPort(self):
        # NOT CRUCIAL
        pass

    def removePort(self, portnum):
        # Removes the port with portnumber portnum (typically 1, 2, 3,...)

        pass

    def addComponent(self, x1, y1, x2, y2, dielectriclayer=0, type="ind", value=10, **kwargs):
        # Adds a SMD definition of TYPE IDEAL in the GEO block (after LORGN)
        # The component type is "ind" for inductor, "cap" for capacitor, or
        # "res" for resistor (or some of their aliases, see below)
        # The value argument sets the inductance/capacitance/resistance
        # The dielectriclayer argument is the dielectric layer index
        # The component's endpoints are (x1,y1) and (x2,y2) in LLC system
        # Only a simple ideal components are supported, thus the following
        # do not appear in the statement of the component: TWTYPE FEED or
        # CUST, TWVALUE, DRP1, PBSHW Y, PBOX, PKG or any TYPE other than IDEAL

        # Map coordinates to Sonnets ULC system
        x1, y1 = self.mapPoint(x1, y1)
        x2, y2 = self.mapPoint(x2, y2)

        if type in ["i", "ind", "inductor", "I", "IND", "INDUCTOR", "L", "l"]:
            nametag = "L"
            type = "IND"
        elif type in ["c", "cap", "capacitor", "C", "CAP", "CAPACITOR"]:
            nametag = "C"
            type = "CAP"
        elif type in ["r", "res", "resistor", "R", "RES", "RESISTOR"]:
            nametag = "R"
            type = "RES"
        else:
            raise self._exception("Invalid argument: {:s}".format(type))

        # Get the number of components and ports prior to this addition
        numberOfComponents = self.getNumberOfPorts(type="component")/2
        numberOfPorts = self.getNumberOfPorts(type="all")

        # Set the default name/label as L1, L2,... for inductors ect.
        defaultName = "\"" + nametag + str(int(numberOfComponents + 1)) + "\""

        # Parameters the user can set with keyword arguments
        dictParams = ({"name": defaultName, # same as label
                        "smdp1_portnum": numberOfPorts + 1,
                        "smdp2_portnum": numberOfPorts + 2,
                        "smdp1_pinnum": 1, # a bit unclear what pinnum is
                        "smdp2_pinnum": 2}) # a bit unclear what pinnum is

        # Update parameters with the user's input
        for key in kwargs.keys():
            if key not in dictParams:
                raise self._exception("Invalid argument: {:s}".format(key))
        dictParams.update(kwargs)

        # Figure out the direction of the component (vertical or horizontal)
        # and define schematic box positions and label position (in the GUI)
        # Note: all positions are relative to upper left corner (ULC)
        sbox_height = abs(x2-x1)/6
        sbox_width = abs(x2-x1)/2

        if y1 == y2 and x1 < x2:
            smdp1_orientation = "L"
            smdp2_orientation = "R"
            leftpos = x1 + sbox_width/2
            rightpos = x2 - sbox_width/2
            toppos = y1 - sbox_height/2
            bottompos = y1 + sbox_height/2
            xpos = x1 + abs(x2-x1)/2
            ypos = toppos

        elif y1 == y2 and x1 > x2:
            smdp1_orientation = "R"
            smdp2_orientation = "L"
            leftpos = x2 + sbox_width/2
            rightpos = x1 - sbox_width/2
            toppos = y1 - sbox_height/2
            bottompos = y1 + sbox_height/2
            xpos = x2 + abs(x2-x1)/2
            ypos = toppos

        elif y1 < y2 and x1 == x2:
            smdp1_orientation = "T"
            smdp2_orientation = "B"
            leftpos = x1 - sbox_height/2
            rightpos = x1 + sbox_height/2
            toppos = y1 + sbox_width/2
            bottompos = y2 - sbox_width/2
            xpos = leftpos
            ypos = y1 + abs(y2-y1)/2

        elif y1 > y2 and x1 == x2:
            smdp1_orientation = "B"
            smdp2_orientation = "T"
            leftpos = x1 - sbox_height/2
            rightpos = x1 + sbox_height/2
            toppos = y2 + sbox_width/2
            bottompos = y1 - sbox_width/2
            xpos = leftpos
            ypos = y2 + abs(y2-y1)/2

        else:
            raise self._exception("Component neither vertical nor horizontal!")

        # Extend the dictionary with more parameters
        dictParams.update({"smdp1_orientation": smdp1_orientation,
                           "smdp2_orientation": smdp2_orientation,
                           "leftpos": leftpos,
                           "rightpos": rightpos,
                           "toppos": toppos,
                           "bottompos": bottompos,
                           "xpos": xpos,
                           "ypos": ypos,
                           "levelnum": dielectriclayer,
                           "smdp1_levelnum": dielectriclayer,
                           "smdp2_levelnum": dielectriclayer,
                           "smdp1_x": x1,
                           "smdp1_y": y1,
                           "smdp2_x": x2,
                           "smdp2_y": y2,
                           "idealtype": type,
                           "compval": value,
                           "objectid": int(numberOfComponents + 1),
                           "gndref": "F",
                           "twtype": "1CELL",
                           "pbshw": "N"})

        # Write component definition to file after LORGN in the GEO block
        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            lorgnIndex = -1
            for index, line in enumerate(contents):
                if line.split()[0] == "LORGN":
                    lorgnIndex = index
                    break
            if lorgnIndex == -1:
                raise self._exception("Cannot find LORGN")

            contents.insert(lorgnIndex + 1, "SMD {levelnum} {name}\n".format(**dictParams))
            contents.insert(lorgnIndex + 2, "ID {objectid}\n".format(**dictParams))
            contents.insert(lorgnIndex + 3, "GNDREF {gndref}\n".format(**dictParams))
            contents.insert(lorgnIndex + 4, "TWTYPE {twtype}\n".format(**dictParams))
            contents.insert(lorgnIndex + 5, "SBOX {leftpos} {rightpos} {toppos} {bottompos}\n".format(**dictParams))
            contents.insert(lorgnIndex + 6, "PBSHW {pbshw}\n".format(**dictParams))
            contents.insert(lorgnIndex + 7, "LPOS {xpos} {ypos}\n".format(**dictParams))
            contents.insert(lorgnIndex + 8, "TYPE IDEAL {idealtype} {compval}\n".format(**dictParams))
            contents.insert(lorgnIndex + 9, "SMDP {smdp1_levelnum} {smdp1_x} {smdp1_y} {smdp1_orientation} {smdp1_portnum} {smdp1_pinnum}\n".format(**dictParams))
            contents.insert(lorgnIndex + 10, "SMDP {smdp2_levelnum} {smdp2_x} {smdp2_y} {smdp2_orientation} {smdp2_portnum} {smdp2_pinnum}\n".format(**dictParams))
            contents.insert(lorgnIndex + 11, "END\n")

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def setComponent(self):
        pass

    def removeComponent(self):
        pass

    ########################################################################
    # TECHNOLOGY AND DIELECTRIC LAYERS (INCL. BOX AND POLYGONS)            #
    ########################################################################
    # Technology layers: TECHLAY in the GEO block and associated polygons
    # Dielectric layers: The lines preceeding the first line of the BOX
    # definition in the GEO block.
    # Anisotropy of the dielectric (in the z direction) is not supported

    def getLayers(self):
        # Returns a list of layer class objects describing each dielectric
        # layer and any technology layers in the dielectric layer

        with open(self._sonnet_file_path + self._sonnet_file, 'r') as fd:
            contents = fd.readlines()
            layers = []

            # Create a list of dielectric layer class objects
            for index, line in enumerate(contents):
                if line.split()[0] == "BOX":
                    layerIndex = 0
                    while contents[index + 1][0] == " ":
                        params = contents[index + 1].split()
                        dlayer = ({"lineindex": index + 1,
                                   "layerindex": layerIndex,
                                   "thickness": float(params[0]),
                                   "erel": float(params[1]),
                                   "mrel": float(params[2]),
                                   "eloss": float(params[3]),
                                   "mloss": float(params[4]),
                                   "esignma": float(params[5]),
                                   "nzpart": int(params[6]),
                                   "name": " ".join(params[7:])})
                        layers.append(_layer(dlayer))
                        layerIndex += 1
                        index += 1
                    break

            # Fill in info about technology layers, ports and components
            for index, line in enumerate(contents):

                # Metal technology layer
                if line.split()[0:2] == ["TECHLAY", "METAL"]:
                    params = contents[index].split()
                    tlayer = ({"lineindex": index,
                               "gds_stream": int(params[4]),
                               "gds_object": int(params[5]),
                               "type": "METAL"})
                    if contents[index + 1] == "MET POL\n":
                        index += 1
                    params = contents[index + 1].split()
                    tlayer.update({"ilevel": int(params[0]),
                                   "nvertices": int(params[1]),
                                   "mtype": int(params[2]),
                                   "filltype": params[3],
                                   "debugid": int(params[4]),
                                   "xmin": float(params[5]),
                                   "ymin": float(params[6]),
                                   "xmax": float(params[7]),
                                   "ymax": float(params[8]),
                                   "conmax": float(params[9]),
                                   "edgemesh": params[12]})
                    layers[tlayer["ilevel"]].recordTechnologyLayer(tlayer)

                # Brick technology layer
                elif line.split()[0:2] == ["TECHLAY", "BRICK"]:
                    params = contents[index].split()
                    tlayer = ({"lineindex": index,
                               "gds_stream": int(params[4]),
                               "gds_object": int(params[5]),
                               "type": "BRICK"})
                    params = contents[index + 2].split()
                    tlayer.update({"ilevel": int(params[0]),
                                   "nvertices": int(params[1]),
                                   "mtype": int(params[2]),
                                   "filltype": params[3],
                                   "debugid": int(params[4]),
                                   "xmin": float(params[5]),
                                   "ymin": float(params[6]),
                                   "xmax": float(params[7]),
                                   "ymax": float(params[8]),
                                   "conmax": float(params[9]),
                                   "edgemesh": params[12]})
                    layers[tlayer["ilevel"]].recordTechnologyLayer(tlayer)

                # Via technology layer
                elif line.split()[0:2] == ["TECHLAY", "VIA"]:
                    params = contents[index].split()
                    tlayer = ({"lineindex": index,
                               "gds_stream": int(params[4]),
                               "gds_object": int(params[5]),
                               "type": "VIA BEGIN"})
                    params = contents[index + 2].split()
                    tlayer.update({"ilevel": int(params[0]),
                                   "nvertices": int(params[1]),
                                   "mtype": int(params[2]),
                                   "filltype": params[3],
                                   "debugid": int(params[4]),
                                   "xmin": float(params[5]),
                                   "ymin": float(params[6]),
                                   "xmax": float(params[7]),
                                   "ymax": float(params[8]),
                                   "conmax": float(params[9]),
                                   "edgemesh": params[12]})
                    params = contents[index + 3].split()
                    tlayer.update({"to_level": int(params[1])})
                    layers[tlayer["ilevel"]].recordTechnologyLayer(tlayer)
                    tlayer["type"] = "VIA END"
                    layers[tlayer["to_level"]].recordTechnologyLayer(tlayer)

                # Port
                elif line.split()[0] == "POR1":
                    currentIndex = index
                    port = ({"lineindex": index,
                             "type": line.split()[1]})
                    while contents[currentIndex].split()[0] != "POLY":
                        currentIndex += 1
                    ipolygon = int(contents[currentIndex].split()[1])
                    params = contents[currentIndex + 2].split()
                    port.update({"ipolygon": ipolygon,
                                 "portnum": int(params[0]),
                                 "resist": float(params[1]),
                                 "react": float(params[2]),
                                 "induct": float(params[3]),
                                 "capac": float(params[4]),
                                 "xcoord": float(params[5]),
                                 "ycoord": float(params[6])})
                    # Find the layer index (ilevel) from ipolygon by finding
                    # the polygon with debugid == ipolygon
                    while contents[currentIndex].split()[0] != "NUM":
                        currentIndex += 1
                    npoly = int(contents[currentIndex].split()[1])
                    for poly in range(npoly):
                        while len(contents[currentIndex].split()) < 13:
                            currentIndex += 1
                        currentIlevel = int(contents[currentIndex].split()[0])
                        currentDebugid = int(contents[currentIndex].split()[4])
                        if currentDebugid == ipolygon:
                            port.update({"ilevel": currentIlevel})
                            break
                        else:
                            currentIndex += 1
                    # Record the port at the found layer
                    layers[port["ilevel"]].recordPort(port)

                # Component
                elif line.split()[0] == "SMD":
                    currentIndex = index
                    component = ({"ilevel": int(line.split()[1]), # levelnum
                                  "name": line.split()[2]}) # label
                    while contents[currentIndex].split()[0] != "TYPE":
                        currentIndex += 1
                    component.update({"type": contents[currentIndex].split()[2],
                                      "x1": int(contents[currentIndex + 1].split()[2]),
                                      "y1": int(contents[currentIndex + 1].split()[3]),
                                      "portnum1": int(contents[currentIndex + 1].split()[5]),
                                      "x2": int(contents[currentIndex + 2].split()[2]),
                                      "y2": int(contents[currentIndex + 2].split()[3]),
                                      "portnum2": int(contents[currentIndex + 2].split()[5])})
                    layers[component["ilevel"]].recordComponent(component)

        # Sanity checks
        gds_stream_list = []
        port_number_list = []
        component_name_list = []
        for layer in layers:
            for tlayer in layer._technology_layers:
                if tlayer["type"] in ["METAL", "BRICK", "VIA BEGIN"]:
                    gds_stream_list.append(tlayer["gds_stream"])
            for port in layer._ports:
                port_number_list.append(port["portnum"])
            for component in layer._components:
                port_number_list.append(component["portnum1"])
                port_number_list.append(component["portnum2"])
                component_name_list.append(component["name"])
        if len(gds_stream_list) != len(set(gds_stream_list)):
            raise self._exception("Error: Several technology layers with the same gds_stream integer!")
        if len(port_number_list) != len(set(port_number_list)):
            raise self._exception("Error: Several ports with the same port number!")
        if len(component_name_list) != len(set(component_name_list)):
            raise self._exception("Error: Several components with the same name!")

        return layers

    def printLayers(self):
        # Prints the layer configuration of the circuit

        layers = self.getLayers()
        print("\n================== TOP ==================\n")
        for layer in layers:
            print("  Dielectric layer:  {:d} ({:s})".format(layer._dielectric_layer["layerindex"], layer._dielectric_layer["name"]))
            for tlayer in layer._technology_layers:
                print("  Technology layer:  {:d} ({:s})".format(tlayer["gds_stream"], tlayer["type"]))
            for port in layer._ports:
                print("  Port:              {:d} ({:s})".format(port["portnum"], port["type"]))
            for component in layer._components:
                print("  Component:         {:s} ({:s})".format(component["name"], component["type"]))
            if layer._dielectric_layer["layerindex"] < len(layers) - 1:
                print("\n================= LVL {:d} =================\n".format(layer._dielectric_layer["layerindex"]))
        print("\n================== GND ==================\n")

    def setTechnologyLayer(self, technologylayer, **kwargs):
        # Set the parameters in a technology layer (but not change type)
        # Mainly for placing technology layers on dielectric layers, e.g.
        # setTechLayer(technologylayer = 23, dielectriclayer = 0)
        # All polygons are overwritten with the parameters of TECHLAY
        # The arguments dielectriclayer and to_dielectriclayer (for vias)
        # specify the destination of the technology layer, which can be
        # 0, 1, 2,... or "up" (moves one up) or "down" (moves one down)

        # Find the technology layer to be manipulated
        layers = self.getLayers()
        lay_type = None
        for layer in layers:
            for tlayer in layer._technology_layers:
                if technologylayer == tlayer["ilevel"] and tlayer["type"] != "VIA END":
                    lay_index = tlayer["gds_stream"]
                    lay_type = tlayer["type"].split()[0]
                    break
        if lay_type == None:
            raise self._exception("Cannot find technology layer: {:d}".format(technologylayer))

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Grab the technology layer parameters from TECHLAY
            currentIndex = lay_index + 1
            if len(contents[currentIndex].split()) < 13:
                currentIndex += 1
            currentLine = contents[currentIndex].split()

            # The following parameters can be changed through kwargs
            dictParams = ({"dielectriclayer": currentLine[0], # same as ilevel
                           "mtype": currentLine[2],
                           "filltype": currentLine[3],
                           "xmin": currentLine[5],
                           "ymin": currentLine[6],
                           "xmax": currentLine[7],
                           "ymax": currentLine[8],
                           "conmax": currentLine[9],
                           "edgemesh": currentLine[12]})

            # Add via parameters
            if lay_type == "VIA":
                viaLine = contents[currentIndex + 1].split()
                dictParams.update({"to_dielectriclayer": viaLine[1], # same as to_level
                                   "meshingfill": viaLine[2],
                                   "pads": viaLine[3]})

            # Update parameters with the user's input
            for key in kwargs.keys():
                if key not in dictParams:
                    raise self._exception("Invalid argument: {:s}".format(key))
            if "dielectriclayer" in kwargs and kwargs["dielectriclayer"] == "up":
                kwargs["dielectriclayer"] = int(dictParams["dielectriclayer"]) - 1
            elif "dielectriclayer" in kwargs and  kwargs["dielectriclayer"] == "down":
                kwargs["dielectriclayer"] = int(dictParams["dielectriclayer"]) + 1
            if  "to_dielectriclayer" in kwargs and  kwargs["to_dielectriclayer"] == "up":
                kwargs["to_dielectriclayer"] = int(dictParams["to_dielectriclayer"]) - 1
            elif "to_dielectriclayer" in kwargs and  kwargs["to_dielectriclayer"] == "down":
                kwargs["to_dielectriclayer"] = int(dictParams["to_dielectriclayer"]) + 1
            dictParams.update(kwargs)

            # Sanity check of diel. layer indices (cannot put techn. layer in bottom diel. layer)
            dlayer = int(dictParams["dielectriclayer"])
            if  dlayer > len(layers) - 2 or dlayer < 0:
                raise self._exception("Invalid argument dielectriclayer: {:d}".format(dlayer))
            if lay_type == "VIA":
                to_dlayer = int(dictParams["to_dielectriclayer"])
                if to_dlayer > len(layers) - 2 or to_dlayer < 0:
                    raise self._exception("Invalid argument to_dielectriclayer: {:d}".format(to_dlayer))

            # Add parameters the user cannot set
            dictParams.update({"nvertices": currentLine[1],
                               "debugid": currentLine[4],
                               "res1": currentLine[10],
                               "res2": currentLine[11]})

            # Update TECHLAY
            currentIndex = lay_index + 1
            if len(contents[currentIndex].split()) < 13:
                currentIndex += 1
            contents[currentIndex] = "{dielectriclayer} {nvertices} {mtype} {filltype} {debugid} {xmin} {ymin} {xmax} {ymax} {conmax} {res1} {res2} {edgemesh}\n".format(**dictParams)
            if lay_type == "VIA":
                contents[currentIndex + 1] = "TOLEVEL {to_dielectriclayer} {meshingfill} {pads}\n".format(**dictParams)

            # Update the associated polygons in NUM
            for index, line in enumerate(contents):
                if line.replace(":"," ").split()[0:2] == ["TLAYNAM", "Stream{:d}".format(technologylayer)]:
                    currentIndex = index - 1
                    if lay_type == "VIA":
                        contents[currentIndex] = "TOLEVEL {to_dielectriclayer} {meshingfill} {pads}\n".format(**dictParams)
                        currentIndex += -1
                    polyParams = contents[currentIndex].split()
                    nvertices, debugid = polyParams[1], polyParams[4]
                    contents[currentIndex] = "{dielectriclayer} {:s} {mtype} {filltype} {:s} {xmin} {ymin} {xmax} {ymax} {conmax} {res1} {res2} {edgemesh}\n".format(nvertices, debugid, **dictParams)

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def setDielectricLayer(self, dielectriclayer=0, **kwargs):
        # Set the parameters in a dielectric layer through kwargs
        # Top dielectric layer is 0, next is 1 and so forth

        # Find the dielectric layer to be manipulated
        layers = self.getLayers()
        layer_index = -1
        for layer in layers:
            if layer._dielectric_layer["layerindex"] == dielectriclayer:
                layer_index = layer._dielectric_layer["lineindex"]
                break
        if layer_index == -1:
            raise self._exception("Cannot find dielectric layer: {:d}".format(dielectriclayer))

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Grab old parameters
            params = contents[layer_index].split()
            if len(params) < 8:
                raise self._exception("Invalid dielectric layer definition")

            # Parameters the user can set
            dictParams = ({"thickness": params[0],
                           "erel": params[1],
                           "mrel": params[2],
                           "eloss": params[3],
                           "mloss": params[4],
                           "esignma": params[5],
                           "name": " ".join(params[7:])})

            # Update parameters with the user's input
            for key in kwargs.keys():
                if key not in dictParams:
                    raise self._exception("Invalid argument: {:s}".format(key))
            dictParams.update(kwargs)

            # Add parameters the user cannot set
            dictParams.update({"nzpart": params[6]})

            # Write the modified dielectric layer to the file
            contents[layer_index] = "      {thickness} {erel} {mrel} {eloss} {mloss} {esignma} {nzpart} \"{name}\"\n".format(**dictParams)

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def removeDielectricLayer(self, dielectriclayer=0):
        # Remove a dielectric layer and associated technology layers
        # Top dielectric layer is 0, next is 1 and so forth

        # Get the layer index and affected technology layers
        layers = self.getLayers()
        lay_index = -1
        tlayersBelow = []
        for layer in layers:
            if layer._dielectric_layer["layerindex"] == dielectriclayer:
                lay_index = layer._dielectric_layer["lineindex"]
                tlayers = layer._technology_layers
            if layer._dielectric_layer["layerindex"] > dielectriclayer:
                for tlayer in layer._technology_layers:
                    tlayersBelow.append(tlayer)
        if lay_index == -1:
            raise self._exception("Invalid dielectriclayer: {:d}".format(dielectriclayer))

        # Update the dielectric layer indices for all technology layers
        # below the deleted dielectric layer
        for tlayer in tlayersBelow:
            lay_name = tlayer["gds_stream"]
            lay_type = tlayer["type"]
            if lay_type in ["METAL", "BRICK", "VIA BEGIN"]:
                self.setTechnologyLayer(lay_name, dielectriclayer = "up")
            elif lay_type == "VIA END":
                self.setTechnologyLayer(lay_name, to_dielectriclayer = "up" )

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Mark line in BOX for deletion
            markedDelete = [lay_index]

            # Mark TECHLAYs for deletion
            tlayerNames = []
            for tlayer in tlayers:
                tlayerNames.append(tlayer["gds_stream"])
                currentIndex = tlayer["lineindex"]
                while contents[currentIndex-1:currentIndex+1] != ["END\n", "END\n"]:
                    markedDelete.append(currentIndex)
                    currentIndex += 1
                markedDelete.append(currentIndex)

            # Remove lines marked for deletion
            markedDelete = list(set(markedDelete))
            markedDelete.sort(reverse=True)
            for index in markedDelete:
                del contents[index]

            for index, line in enumerate(contents):
                # Update the number of levels in BOX: nlev -> nlev - 1
                if line.split()[0] == "BOX":
                    nlev = int(line.split()[1]) - 1
                    contents[index] = "BOX {:d} ".format(nlev) + " ".join(line.split()[2:]) + "\n"
                # Delete polygons associated with deleted technology layers
                if line.split()[0] == "TLAYNAM" and \
                   line.replace(":"," ").split()[1] in ["Stream{:d}".format(name) for name in tlayerNames]:
                    # Delete lines above TLAYNAM line
                    currentIndex = index
                    while contents[currentIndex].split()[0] not in ["NUM", "END"]:
                        del contents[currentIndex]
                        currentIndex += -1
                    # Delete lines below TLAYNAM line (polygon coordinates)
                    currentIndex += 1
                    while contents[currentIndex] != "END\n":
                        del contents[currentIndex]
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def removeEmptyDielectricLayers(self):
        # Removes all dielectric layers that does not contain any technology
        # layers except the bottom dielectric layer, which should be empty

        layers = self.getLayers()
        numberOfNonEmptyLayers = 0

        for layer in layers[0:-1]:
            if len(layer._technology_layers) == 0:
                self.removeDielectricLayer(numberOfNonEmptyLayers)
            else:
                numberOfNonEmptyLayers += 1

    def shiftPolygons(self, xshift, yshift):
        # Shifts the positions of all polygons by (xshift, yshift) in LLC system

        # Map the relative coordinates to Sonnet's ULC system
        xshift, yshift = xshift, -yshift

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            numIndex = -1
            for index, line in enumerate(contents):
                if line.split()[0] == "NUM":
                    numIndex = index
                    npoly = int(contents[numIndex].split()[1])
                    break
            if numIndex == -1:
                raise self._exception("Cannot find NUM")

            # Start at the NUM definition and loop over polygons
            index = numIndex
            for poly in range(npoly):
                # Jump to the line with nvertices
                while len(contents[index].split()) < 5:
                    index += 1
                nvertices = int(contents[index].split()[1])
                # Jump to the first xvertex and yvertex
                while len(contents[index].split()) != 2:
                    index += 1
                # Shift all coordinates in the polygon
                startindex = index
                for index in range(startindex, startindex + nvertices):
                    coordinates = contents[index].split()
                    coordinates[0] = "{:f}".format(float(coordinates[0]) + xshift)
                    coordinates[1] = "{:f}".format(float(coordinates[1]) + yshift)
                    contents[index] = " ".join(coordinates) + "\n"

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def setBox(self, **kwargs):
        # Set the parameters of the BOX to the values specified in kwargs

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            boxIndex = -1
            for index, line in enumerate(contents):
                if line.split()[0] == "BOX":
                    boxIndex = index
                    break
            if boxIndex == -1:
                raise self._exception("Cannot not find BOX")

            # Grab old parameters
            params = contents[boxIndex].split()
            if len(params) < 6:
                raise self._exception("Invalid BOX definition")

            # Parameters the user can set
            dictParams = ({"xwidth": params[2],
                           "ywidth": params[3],
                           "xcells2": params[4],
                           "ycells2": params[5],
                           "eeff": params[7]})

            # Update parameters with the user's input
            for key in kwargs.keys():
                if key not in dictParams:
                    raise self._exception("Invalid argument: {:s}".format(key))
            dictParams.update(kwargs)

            # Update with parameters the user cannot set
            dictParams.update({"nlev": params[1],
                               "nsubs": params[6]})

            # Write the modified BOX definition to the file
            contents[boxIndex] = "BOX {nlev} {xwidth} {ywidth} {xcells2} {ycells2} {nsubs} {eeff}\n".format(**dictParams)

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def cropBox(self, xcellsize=1, ycellsize=1):
        # Crops the BOX to the circuit and set the cellsize in x and y direction, and
        # sets the local origin (LORGN in GEO block) in order to place point correctly
        # If the circuit is rectangular, this ensures that ports added to the
        # edges of the circuit is also at the edge of the BOX

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Get LORGN and NUM indices
            lorgnIndex = -1
            numIndex = -1
            for index, line in enumerate(contents):
                if line.split()[0] == "LORGN":
                    lorgnIndex = index
                elif line.split()[0] == "NUM":
                    numIndex = index
                    npoly = int(contents[numIndex].split()[1])
            if lorgnIndex == -1:
                raise self._exception("Cannot find LORGN")
            if numIndex == -1:
                raise self._exception("Cannot find NUM")

            # Start at the NUM definition and loop over polygons
            index = numIndex
            xlist = []
            ylist = []
            for poly in range(npoly):
                # Jump to the line with nvertices
                while len(contents[index].split()) < 5:
                    index += 1
                nvertices = int(contents[index].split()[1])
                # Jump to the first xvertex and yvertex
                while len(contents[index].split()) != 2:
                    index += 1
                # Get all the polygon coordinates
                startindex = index
                for index in range(startindex, startindex + nvertices):
                    coordinates = contents[index].split()
                    xlist.append(float(coordinates[0]))
                    ylist.append(float(coordinates[1]))

            # Get circuit dimensions and redefine the local origin (LORGN)
            xmin, ymin, xmax, ymax = min(xlist), min(ylist), max(xlist), max(ylist)
            contents[lorgnIndex] = "LORGN {:f} {:f} U\n".format(0, ymax - ymin)

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

        # Shift the circuit (all polygons, standard ports and components)
        self.shiftPorts(-xmin, ymin)
        self.shiftPolygons(-xmin, ymin)

        # Resize BOX to the circuit's dimensions
        self.setBox(xwidth = xmax - xmin, ywidth = ymax - ymin, \
                    xcells2 = int(2*(xmax - xmin)/xcellsize), \
                    ycells2 = int(2*(ymax - ymin)/ycellsize))

    ########################################################################
    # SWEEPS                                                               #
    ########################################################################
    # Parameter sweeps, frequency sweeps ect. are defined in their respective
    # blocks. The CONTROL block sets which sweep is presently set to run
    # during the simulation. Only one sweep is set at a time.

    def setControl(self, sweep, **kwargs):
        # Sets the CONTROL block with the parameters in kwargs and the
        # current sweep. Defines the CONTROL block if it doesn't exist.

        if sweep not in ["simple", "std", "abs", "optimize", "varswp", "extfile"]:
            raise self._exception("Invalid sweep argument: {:s}".format(sweep))

        # Create dictionary with default values
        dictParams = ({"res_abs": None, # only for ABS sweeps
                       "options": "-d",
                       "subsplam": None, # optional
                       "edgecheck": None, # optional
                       "cfmax": None, # optional
                       "cepsy": None, # optional
                       "filename": None, # only for EXTFILE sweeps
                       "speed": 1,
                       "res_abs": None, # optional
                       "cache_abs": 1,
                       "targ_abs": 300, # only for ABS sweeps
                       "q_acc": "Y",
                       "det_abs_res": None}) # optional

        # Update parameters with the user's input
        for key in kwargs.keys():
            if key not in dictParams:
                raise self._exception("Invalid argument: {:s}".format(key))
        dictParams.update(kwargs)

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            controlExists = False
            for index, line in enumerate(contents):
                if line == "CONTROL\n":
                    controlExists = True
                    currentIndex = index
                    # Update the CONTROL block if it exists
                    while "END CONTROL\n" != contents[currentIndex]:
                        # The sweep statement defining the current sweep
                        if contents[currentIndex].split()[0] in \
                            ["SIMPLE", "STD", "ABS", "OPTIMIZE", "VARSWP", "EXTFILE"]:
                            contents[currentIndex] = sweep.upper() + "\n"
                        # Update parameters present in the CONTROL block
                        for key, value in dictParams.items():
                            if value != None and contents[currentIndex].split()[0] == key.upper():
                                contents[currentIndex] = key.upper() + " " + str(value) + "\n"
                                dictParams[key] = None
                        currentIndex += 1
                    # Insert parameters not already present in the CONTROL block
                    for key, value in dictParams.items():
                        if value != None:
                            contents.insert(currentIndex - 1, key.upper() + " " + str(value) + "\n")
                            dictParams[key] = None
                            currentIndex += 1
                    break

            # Create a default CONTROL block if it does not exist
            if controlExists == False:
                for index, line in enumerate(contents):
                    if line == "END DIM\n":
                        currentIndex = index
                        contents.insert(currentIndex + 1, "CONTROL\n")
                        contents.insert(currentIndex + 2, sweep.upper() + "\n")
                        currentIndex += 3
                        for key, value in dictParams.items():
                            if value != None:
                                contents.insert(currentIndex, key.upper() + " " + str(value) + "\n")
                                currentIndex += 1
                        contents.insert(currentIndex, "END CONTROL\n")
                        break

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def setFrequencySweep(self, f1=5, f2=8, fstep=None):
        # Redefines or adds the FREQ block with a single frequency sweep, and
        # sets this sweep as the current sweep in the CONTROL block
        # Currently, the following sweep types are implemented:
        # SIMPLE: Linear sweep from f1 to f2 in steps fstep if fstep is speficied
        # ABS: Adaptive sweep from f1 to f2 if fstep is left unspecified (None)

        if fstep == None:
            sweepType = "ABS"
            insertStr = "ABS {:f} {:f}\n".format(f1, f2)
        elif fstep >= 0 and fstep < abs(f1 - f2):
            sweepType = "SIMPLE"
            insertStr = "SIMPLE {:f} {:f} {:f}\n".format(f1, f2, fstep)
        else:
            raise self._exception("Invalid frequency sweep definition")

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Overwrite the FREQ block if it exists
            freqExists = False
            for index, line in enumerate(contents):
                if line == "FREQ\n":
                    freqExists = True
                    contents.insert(index + 1, insertStr)
                    while "END FREQ\n" != contents[index + 2]:
                        del contents[index + 2]
                    break

            # Add the FREQ block after the DIM block if it does not exists
            if freqExists == False:
                for index, line in enumerate(contents):
                    if line == "END DIM\n":
                        contents.insert(index + 1, "FREQ\n")
                        contents.insert(index + 2, insertStr)
                        contents.insert(index + 3, "END FREQ\n")
                        break

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

        # Set the CONTROL block
        self.setControl(sweepType.lower(), options="-d", speed=1, cache_abs=1,\
            targ_abs=300, q_acc="N")

    def setParameterSweep(self, parameter, pmin, pmax, pstep, **kwargs):
        # Redefines or adds the VARSWP block with a single parameter sweep, and
        # sets this sweep as the current sweep in the CONTROL block.
        # The parameter argument must match a name of an ideal component,
        # which by default are named L1, L2,... for inductors and similarly
        # C1, C2,... for capacitors and R1, R2,... for resistors.
        # Only adaptive (ABS_ENTRY) and linear (SWEEP) freq. sweeps supported
        # The freq. sweep type is taken from the FREQ block if it exists,
        # or (with higher priority) from the kwargs with the following rule:
        # SIMPLE: Linear sweep from f1 to f2 in steps fstep if fstep is speficied
        # ABS: Adaptive sweep from f1 to f2 if fstep is left unspecified (None)

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Set the value of the component as the variabel
            names = []
            parameterMatched = False
            for index, line in enumerate(contents):
                # Find components definitions
                if line.split()[0] == "SMD":
                    name = line.replace("\"","").split()[2]
                    names.append(name)
                    # If we find the components whose value we will sweep
                    if parameter == name:
                        parameterMatched = True
                        currentIndex = index
                        while contents[currentIndex].split()[0:2] != ["TYPE", "IDEAL"]:
                            currentIndex += 1
                        # Set compval to "name" (the variabel name)
                        [comptype, compval] = contents[currentIndex].split()[2:4]
                        contents[currentIndex] = "TYPE IDEAL {:s} \"{:s}\"\n".format(comptype, name)
                        break
            if parameterMatched == False:
                raise self._exception("Parameter \'{:s}\' does not match any component name: {:s}".format(parameter, str(names)))

            # Define the variabel as a VALVAR statement after the TECHLAYs
            techlayFound = False
            for index, line in enumerate(contents):
                if line.split()[0] == "TECHLAY":
                    techlayFound = True
                if techlayFound == True and contents[index-1:index+1] == ["END\n", "END\n"] \
                    and contents[index + 1].split()[0] != "TECHLAY":
                    contents.insert(index + 1, "VALVAR {:s} {:s} {:s} \"\"\n".format(parameter, comptype, str(pmin)))
                    break

            # Prepare default parameters for the VARSWP block
            dictParams = ({"f1": 5,
                           "f2": 8,
                           "fstep": None,
                           "ytype": "Y"})

            # If the FREQ block exists then copy the frequency sweep settings
            for index, line in enumerate(contents):
                if line == "FREQ\n":
                    freqParams = contents[index+1].split()
                    if freqParams == "ABS":
                        dictParams["f1"] = freqParams[1]
                        dictParams["f2"] = freqParams[2]
                    elif freqParams == "SIMPLE":
                        dictParams["f1"] = freqParams[1]
                        dictParams["f2"] = freqParams[2]
                        dictParams["fstep"] = freqParams[3]
                break

            # Update parameters with the user's input
            for key in kwargs.keys():
                if key not in dictParams:
                    raise self._exception("Invalid argument: {:s}".format(key))
            dictParams.update(kwargs)

            dictParams.update({"parameter": parameter,
                               "min": pmin,
                               "max": pmax,
                               "step": pstep})

            # Sanity check of input
            [f1, f2, fstep] = [float(dictParams["f1"]), float(dictParams["f2"]), dictParams["fstep"]]
            if fstep != None and float(fstep) > 0 and float(fstep) < abs(f1 - f2) and f1 < f2:
                sweeptypeStr = "SWEEP {f1} {f2} {fstep}\n".format(**dictParams)
            elif fstep == None and f1 < f2:
                sweeptypeStr = "ABS_ENTRY {f1} {f2}\n".format(**dictParams)
            else:
                raise self._exception("Invalid frequency sweep definition")
            varswpStr = "VAR {parameter} {ytype} {min} {max} {step}\n".format(**dictParams)

            # Overwrite the VARSWP block if it exists
            varswpExists = False
            for index, line in enumerate(contents):
                if line == "VARSWP\n":
                    varswpExists = True
                    contents.insert(index + 1, sweeptypeStr)
                    contents.insert(index + 2, varswpStr)
                    while "END VARSWP\n" != contents[index + 3]:
                        del contents[index + 3]
                    break

            # Add the VARSWP block after the GEO block if it does not exists
            if varswpExists == False:
                for index, line in enumerate(contents):
                    if line == "END GEO\n":
                        contents.insert(index + 1, "VARSWP\n")
                        contents.insert(index + 2, sweeptypeStr)
                        contents.insert(index + 3, varswpStr)
                        constens.insert(index + 4, "END\n")
                        contents.insert(index + 5, "END VARSWP\n")
                        break

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

        # Set the CONTROL block
        self.setControl("varswp", options="-d", speed=1, cache_abs=1, \
            targ_abs=300, q_acc="Y")

    ########################################################################
    # OUTPUT FILE AND DATA PLOTTING                                        #
    ########################################################################
    # Output file format in the FILEOUT block and extraction from file.

    def setDataFile(self, filename):
        self._data_file = filename

    def setDataFilePath(self, path):
        self._data_file_path = path

    def setOutput(self, **kwargs):
        # Creates or overwrites the FILEOUT block which specifies the
        # file format of the output data file. By default a single
        # spreadsheet file is creted with Sij data in dB-angle format.
        # Only a geometry project output file of "Response" type is implemeted.

        # Create a dictionary with default parameters (see .son manual p. 61)
        dictParams = ({"filetype": "csv",
                       "embed": "D",
                       "abs_inc": "Y",
                       "filename": "$BASENAME.csv", # $BASENAME = name of son file
                       "comments": "NC",
                       "sig": 8,
                       "partype": "S",
                       "parform": "DB",
                       "ports": "R 50",
                       "folder": ""}) # folder relative to son file, e.g. "data"

        # Update parameters with the user's input
        for key in kwargs.keys():
            if key not in dictParams:
                raise self._exception("Invalid argument: {:s}".format(key))
        dictParams.update(kwargs)

        # Sanity check of input
        for key in ["filetype", "embed", "abs_inc", "filename", "comments", \
            "partype", "parform", "ports", "folder"]:
            if type(dictParams[key]) is not str:
                raise self._exception("Value of \"{:s}\" must be a string".format(key))

        # Set parameters that go into the son file in upper case
        for key in ["filetype","embed", "abs_inc", "comments", "partype", "parform", "ports"]:
            dictParams[key] = dictParams[key].upper()

        # More sanity checks
        if dictParams["filetype"] not in ["TS", "TOUCH2", "DATA_BANK", "SC", "CSV", "CADENCE", "MDIF", "EBMDIF"]:
            raise self._exception("Invalid \"filetype\": {filetype}".format(*dictParams))
        if dictParams["embed"] not in ["D", "ND"]:
            raise self._exception("Invalid \"embed\": {embed}".format(*dictParams))
        if dictParams["abs_inc"] not in ["Y", "N"]:
            raise self._exception("Invalid \"abs_inc\": {abs_inc}".format(*dictParams))
        if dictParams["comments"] not in ["NC", "IC"]:
            raise self._exception("Invalid \"comments\": {comments}".format(*dictParams))
        if dictParams["sig"] not in [8, 15]:
            raise self._exception("Invalid \"sig\": {sig}".format(**dictParams))
        if dictParams["partype"] not in ["S", "Y", "Z"]:
            raise self._exception("Invalid \"partype\": {partype}".format(*dictParams))
        if dictParams["parform"] not in ["MA", "DB", "RI"]:
            raise self._exception("Invalid \"parform\": {parform}".format(*dictParams))
        if dictParams["ports"].split()[0] not in ["R", "Z", "TERM", "FTERM"] \
            or len(dictParams["ports"].split()) < 2:
            raise self._exception("Invalid \"ports\": {ports}".format(*dictParams))

        # Set data file path and data file
        filename = dictParams["filename"].replace("$BASENAME", self._sonnet_file[:-4])
        if dictParams["folder"] == "":
            self.setDataFilePath(self._sonnet_file_path + "\\")
        else:
            self.setDataFilePath(self._sonnet_file_path + dictParams["folder"] + "\\")
        self.setDataFile(filename)

        # Prepare strings to be inserted
        fileStr = "{filetype} {embed} {abs_inc} {filename} {comments} {sig} {partype} {parform} {ports}\n".format(**dictParams)
        folderStr = "FOLDER {folder}\n".format(**dictParams)

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            fileoutExists = False
            for index, line in enumerate(contents):
                # Overwrite the FILEOUT block if it exists
                if line == "FILEOUT\n":
                    fileoutExists = True
                    contents.insert(index + 1, fileStr)
                    contents.insert(index + 2, folderStr)
                    while "END FILEOUT\n" != contents[index + 3]:
                        del contents[index + 3]
                    break

            # Create the FILEOUT block if it does not exist
            if fileoutExists == False:
                for index, line in enumerate(contents):
                    if line == "END GEO\n":
                        currentIndex = index
                    elif line == "END OPT\n":
                        currentIndex = index
                    elif line == "END VARSWP\n":
                        currentIndex = index
                        break

                contents.insert(index + 1, "FILEOUT\n")
                contents.insert(index + 2, fileStr)
                contents.insert(index + 3, folderStr)
                contents.insert(index + 4, "END FILEOUT\n")

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def getOutput(self, data="frequency", run=1):
        # Look for a csv file containing data, return a list with the data
        # specified by the user. The argument data can either be "frequency"
        # or a valid response data type from the csv file, e.g. "MAG[S12]"...
        # If the data contains a parameter sweep, then run is an integer
        # that specifies the sweep number (run number) to be plotted.

        # Verify that the data file exists
        file_found = 0
        for root, dirs, files in os.walk(self._data_file_path):
            for file in files:
                # Make search case insensitive
                if self._data_file.lower() == file.lower():
                    file_found = 1

        if (file_found == 0):
            print("Project file %s can not be located in path %s"%(self._data_file,self._data_file_path))
            raise self._exception("Data file not found! Check that directory and filename are correct!")

        with open(self._data_file_path + self._data_file, 'r') as fd:
            # Data files might be big, so we do not load the entire file

            currentRun = 1
            for line in fd:
                if line[0:9] == "Frequency" and currentRun < run:
                    currentRun += 1
                elif line[0:9] == "Frequency" and currentRun == run:
                    # Now we are at the beginning of our data block:
                    # Let's find the correct data row
                    params = line.replace("\n","").split(",")
                    if data.upper() in ["F", "FREQ", "FREQUENCY"]:
                        index = 0
                    else:
                        index = params.index(data)
                    break

            # Skip all lines containing "=", i.e. paramter sweep lines
            line = fd.readline()
            while "=" in line:
                line = fd.readline()

            # Collect plot data from the data block
            datalist = []
            while line != "" and line[0] != "!":
                datalist.append(float(line.split()[index]))
                line = fd.readline()

            return datalist


    ########################################################################
    # MISCELLANEOUS FUNCTIONS                                              #
    ########################################################################

    def addComment(self, string):
        # Add string as a comment at the top of the Sonnet project file
        # Comments in Sonnet project files start with "!"

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()
            contents.insert(0, "! " + string + "\n")
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def mapPoint(self, xcoord, ycoord):
        # Sonnet computes points relative to the circuit's upper left corner (ULC),
        # but it's easier for the user to specify points relative to the lower
        # left corner (LLC). This function takes an input point (xcoord, ycoord)
        # from the user's LLC system and returns the point in Sonnet's ULC system

        with open(self._sonnet_file_path + self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Get the NUM index
            numIndex = -1
            for index, line in enumerate(contents):
                if line.split()[0] == "NUM":
                    numIndex = index
                    npoly = int(contents[numIndex].split()[1])
                    break
            if numIndex == -1:
                raise self._exception("Cannot find NUM")

            # Start at the NUM definition and loop over polygons
            index = numIndex
            ylist = []
            for poly in range(npoly):
                # Jump to the line with nvertices (i.e. with a least 5 entries)
                while len(contents[index].split()) < 5:
                    index += 1
                nvertices = int(contents[index].split()[1])
                # Jump to the first xvertex and yvertex
                while len(contents[index].split()) != 2:
                    index += 1
                # Get all the polygon coordinates
                startindex = index
                for index in range(startindex, startindex + nvertices):
                    coordinates = contents[index].split()
                    ylist.append(float(coordinates[1]))

            # Get circuit dimensions
            ymin, ymax = min(ylist), max(ylist)

        return xcoord, (ymax - ymin) - ycoord

    def runMakeover(self):
        # Applies a series of functions that takes to gds file into a
        # Sonnet file ready for adding ports and simulation

        # Convert .gds to .son
        self.runGdsTranslator()
        # Set the Sonnet file name to the same as the gds file
        self.setSonnetFile(self._gds_file[:-3] + "son")
        # Set the Sonnet file path to the same as the gds file path
        self.setSonnetFilePath(self._gds_file_path)
        # Crop the bounding box to the circuit
        self.cropBox()
        # Add comment
        self.addComment("The EQuS custom Sonnet makeover has been performed")
        # Remove all empty layers except the bottom layer, which should be empty
        self.removeEmptyDielectricLayers()

        # Set the dielectric layers to our standard settings
        layers = self.getLayers()
        if len(layers) < 2:
            raise self._exception("Device contains less than two dielectric layers! Expected one bottom layer and at least one vacuum layer on top.")
        if len(layers) > 3:
            raise self._exception("Device contains more that three dielectric layers! Expected either zero or one air bridge.")
        # Set the bottom dielectric layer to Silicon
        bottomDielectricLayer = layers[-1]._dielectric_layer["layerindex"]
        self.setDielectricLayer(bottomDielectricLayer, \
            thickness=279,\
            erel=11.45,\
            mrel=1,\
            eloss=1e-006,\
            mloss=0,\
            esignma=0.00044,\
            name="Silicon (EQuS)")
        # If there is a air bridge, set the next layer to a thin vacuum layer
        if len(layers) > 2:
            airBridgeLayer = layers[-2]._dielectric_layer["layerindex"]
            self.setDielectricLayer(airBridgeLayer, \
                thickness=2.9,\
                erel=1,\
                mrel=1,\
                eloss=0,\
                mloss=0,\
                esignma=0,\
                name="Vacuum")
        # Set the top layer to a thick vacuum layer
        self.setDielectricLayer(0, \
            thickness=500,\
            erel=1,\
            mrel=1,\
            eloss=0,\
            mloss=0,\
            esignma=0,\
            name="Vacuum")

        # Make sure to get an output file with data
        self.setOutput()





'''
TO DO:
    Generalize runMakeover to suit any realistic situation
X   Get output data by defining a OUTPUT FILE block
    Clean up exceptions and error messages in code (kill all print statements)
    Clean up string formatting in code to comply with new style
-   Use flake8 style to clean up code style & make documentation
X   Support VIA and BRICK technology layers TECHLAY
X       --> how does parameters in TECHLAY influence NUM?
X       --> should the to_layer and ilevel options be more user friendly? (better default values?)
X   Support VIA and BRICK polygons in NUM
X   addPort: make it more userfriendly to pick other attachment points, for
X       instance by specifying which layer to attach to (what will be used?)
X       Search nearby attachement points
    addPort: As of now the xcoord,ycoord are not changed to lie on edge, will that give an error?
    setFile/Filepath: / can be used instead of \\. Append / if the user forgets.
X   get a list of gds layers directly from the gds file
X   removeDielectricLayer: nlev -> nlev-1 in BOX statement
    When simulating on a server, we should not monitor processes locally on the computer
X   Map techlayer onto dielectric layer:  setTechLayerDielectric(techlayer = 23, dielectriclayer = 0)
X       with techlayer index from gdspy
X   Dictionary/list of techlayers (indexed by stream/gds) and dielectric layers (0,1,...)
X   String/integer bug in lines like "layer == "bottom" or layer >= len(layerIndex)"
X   Kill all "END GEO\n" break statements: END GEO is almost at the end of the file, redundant to look for
-   Use filepathjoin from os to figure out automatically linux and windows filepath style
X   Ability to sweep parameters inside Sonnet
X   Include components and ports in the layer class, and print them in printLayers
    Include layer contents as dictionaries instead of lists (more printing flexibilty and nicer code)
    Remove or shift components and ports when deleting layers
X   Bug: Must be able to handle StreamN:M where M != 1
X   Make a function that removes all empty layers
    Bharath: set template


    IDEAS FOR FUTURE DEVELOPMENT:
    Instead of reading and writing to the son file in every function, one can
    read the converted file into an class instance of a son file. All ports,
    layers, polygons ect. are represented as dictionaries which allows for an
    easy way to change the parameters. Say the user removes a layer, then
    it is easy to remove/change the affected ports, layers ect. just by
    changing the dictionaries. No reading and writing from file is necessary.
    Only just before the simulation runs do we write an actual son file.
'''


"""
    MORE INFORMATION ON THE SONNET PROGRAMS (em.exe and gds.exe)

   Sonnet command: em -[options] <project name> [external frequency file]

      where:

   <options> is one or more of the run options shown in the table below. If you use
   multiple options they should be typed with no spaces in between after the minus
   sign. Note that other run options may be set in the Analysis Setup dialog box for
   your project and will be used during the analysis.

   <project name> is the name of the project which you wish to analyze. If there is
   no extension, then the extension ".son" is assumed. This field is required

   [external frequency file] is the name of an optional external frequency control
   file whose extension is ".eff". This extension must be included when specifying
   the control file. You may create an external frequency control file in the project
   editor. For details see Frequency Sweep Combinations in online help in the project
   editor. The frequencies in this file override the frequencies in the project.


   Option Meaning

   -Dlicense Used for debugging em licensing problems. Displays all environment
   information relevant to licensing.

   -N Display number of subsections and estimated required memory. Em
   then exits without running a full analysis.

   -test Run em on a test circuit. Used to verify that em can get a license and
   run successfully.

   -v Display analysis information as the analysis is performed. The
   analysis information is output to the command prompt window or
   terminal from which the batch was executed.

   -AbsCacheNone Disable ABS caching (overrides setting in project file).

   -AbsCacheStopRestart Enable ABS stop-restart caching (overrides setting in project file).

   -AbsCacheMultiSweep Enable ABS multi-sweep plus stop-restart caching (overrides project
   file).

   -AbsNoDiscrete Used when running ABS with pre-existing cache data. Tells the
   analysis engine not to do any more discrete frequencies. If preexisting
   cache data is sufficient to get converged ABS solution, then
   that solution is written to output. Otherwise, no processing is
   performed.

   -SubFreqHz[value] where [value] is the subsectioning frequency in Hz. Note there is no
   space before the value field.
   This option allows subsectioning frequency to be specified on the
   command line, thereby overriding the settings in the project file.

   -ParamFile <filename> where <filename> is the name of a file which contains the value(s)
   which you wish to use for parameter(s) in the circuit being analyzed.
   These values override the value contained in the geometry project for
   the analysis, but do not change the contents of the geometry project.
   The syntax for the parameter file is <parname>=fnum where
   <parname> is the name of the parameter and fnum is a floating point
   number which defines the value of the parameter for the analysis.

   -64BitThresh<mem> Memory threshold in MB to enable the 64-bit solver where <mem>
   contains an integer value identifying the memory threshold at which
   64-bit processing is used. If this command is not used the threshold is
   set to 3600 Mbytes (3.6 Gbytes).

   -64BitForce This option forces the analysis to use 64-bit processing regardless of
   how much memory is required to analyze your circuit; the memory
   threshold is not used.

   -32BitForce This option forces the analysis to use 32-bit processing regardless of
   how much memory is required to analyze your circuit; the memory
   threshold is not used.


Added by njsloft after running programs in Sonnet's bin folder in command line with -h option.
Notice: emgraph and emstatus has no option -h, so I don't know the options for these programs.


Usage:  em [ -options ] <project file> [external frequency file]

  Command line options:
  -Dlicense    Display debugging information for licensing problems.
  -h           Display this help information.
  -N           Display number of subsections and memory estimate.
  -test        Run em on an internal test circuit.
  -v           Verbose mode. Display messages during program execution.
  -ver         Display the em version.


gds [options] gdsfile

  -v             - Verbose output
  -d             - Print list of structures in file
  -p structname  - Convert structure structname instead of default structure.
  -P default     - Converts default structure, either "first", "last", or "best"
  -L             - Create a layer file for user. Gds file not converted.
  -R             - Remove empty layers when creating layer file.
  -1             - Create single layer file.
  -l layerfile   - Input using layer file.
  -g             - Use project file for circuit information.
  -q             - Use project file for circuit information (appends to existing geometry).
  -i project     - Use project for input.
  -o project     - Output using project file.
  -y             - Invert the coordinates over the X-axis.
  -r             - Convert vias to simplified vias
  -t <type>      - Translate coordinates
     none          - no tranlation
     min           - move min x,y coordinates so it is a 0,0
     normal        - move min x,y coordinates so it is in substrate
     x,y           - move x,y coordiante
  -s <type>      - Create substrate
     max           - use max_x,max_y as size of substrate
     min           - make substrate the smallest possible
     normal        - make substrate large enough so that the
                   - circuit is away from the wall. (default)
     width,height  - make substrate width and height size
  -c <type>      - Specify conversion control option for zero width paths
     boundary_path     - Converts paths to boundaries, assuming that each point
                         is an endpoint (default)
     no_boundary_path  - Do not convert paths to boundaries.  Will make zero
                         width lines by tracing each line to end then back
                         to the beginning.  Note that these polygons have
                         no subsections.
     smart_path        - Makes a path into a boundary path if the end point
                          equals the begin point.  Else makes it a
                          no_boundary_path
  -m left,right,top,bottom    - Set margin for circuit
  -k boxsize     - Only output polygons that are entirely in the box.
                   Format of box is X1,X2,Y1,Y2
  -b Width,Height - Do not output polygons which are smaller than height and width
  -B %Width,%Height - Same as -b options except width and height are in terms
                 - of percentage of the entire circuit
  -C Width,Height- Set output project cell size
  -W             - Suppresses warning messages.
  -z file        - Print list of structures and put results into file
  -M file        - Set the material file.
  -D n           - Set debug level
  -F             - Output record identification format.
  -A             - Use Ascii file input
  -T File        - Set trace file
  -S             - Output abbreviate (short) record format.
  -G File        - Create gds file from ASCII input
  -j             - Create via pads
  -J type        - Specify the via meshing fill (Full, Ring(default), Vertices or Center)
  -x box         - Exclude converting box elements
  -Q             - For box elements, force BOXTYPE values to 0
  -e             - Make tech layers
  -V             - Prints program version
  -h             - Prints this help message.

"""
