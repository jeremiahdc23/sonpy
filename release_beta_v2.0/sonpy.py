# -*- coding: utf-8 -*-

import subprocess
import time
import os
from win32com.client import GetObject # outcomment only on Linux!

# PROGRAM: SonPy
# VERSION: $\beta$ 2.0 (May >21 2018)
# PURPOSE: Python interface for Sonnet.

class sonnet(object):
   # Class for interactions between Sonnet and Python
   # Tested on Windows, can be extended to Linux (but not Mac)

    def __init__(self):
        # Settings for em simulator
        self._exception = Exception
        self._executable_path = 'C:\\Program Files (x86)\\Sonnet Software\\14.54\\bin\\'
        self._executable_file = 'em.exe'
        self._executable_and_monitor_file = 'emstatus.exe'
        self._executable_and_monitor_options = '-Run'
        self._sonnet_file_path = 'C:\\Users\\Lab\\Desktop\\sonnet_test\\'
        self._sonnet_file = 'test.son'
        self._sonnet_options = '-v'
        self._done_flag = 1
        self._run_count = 0
        self._output = None
        self._em_process = None
        self._emstatus_process = None
        self._parentPID = None
        self._emPID = None
        self._winprocessParent = None

        # Settings for .gds to .son translator
        self._gds_translator_file = 'gds.exe'
        self._gds_translator_options = '-v'
        self._gds_file_path = self._sonnet_file_path
        self._gds_file = 'test.gds'
        self._gds_process = None

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

    ########################################################################
    # PORTS AND COMPONENTS                                                 #
    ########################################################################
    # Standard ports: POR1 in the GEO block. Only type=STD is supported.
    # Ideal components: SMD in the GEO block. Only ideal components are supported.

    def getNumberOfPorts(self, type="all"):
        # Returns the number of ports of the specified type where type can be
        # "port" (POR1/regular ports), "component" (SMD/components), or "all" (POR1 and SMD)

        numberOfPorts = 0

        if type not in ["all", "port", "component"]:
            raise self._exception("Invalid port type: {:s}".format(type))

        with open(self._sonnet_file_path+self._sonnet_file, 'r') as fd:
            contents = fd.readlines()
            # Find POR1 and SMD definitions
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                elif line.split()[0] == "SMD" and type in ["all", "component"]:
                    numberOfPorts += 2 # two ports for each ideal component
                elif line.split()[0] == "POR1" and type in ["all", "port"]:
                    numberOfPorts += 1

        return numberOfPorts

    def shiftPorts(self, xshift, yshift):
        # Shifts the positions of all POR1 STD ports by (xshift, yshift)
        # with respect to LLC

        # Map coordinates to Sonnets ULC system
        xshift, yshift = self.mapPoint(xshift, yshift)

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                elif line == "POR1 STD\n":
                    # Grab and update the position of the port
                    params = contents[index + 3].split()
                    params[5] = "{:f}".format(float(params[5]) + xshift)
                    params[6] = "{:f}".format(float(params[6]) + yshift)
                    contents[index + 3] = " ".join(params) + "\n"

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def shiftComponents(self, xshift, yshift):
        # Shifts the positions of all components by (xshift, yshift)
        # with respect to LLC

        # Map coordinates to Sonnets ULC system
        xshift, yshift = self.mapPoint(xshift, yshift)

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                elif line.split()[0] == "SMD":
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

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def addPort(self, xcoord, ycoord, specify_polygon=False, **kwargs):
        # Add a POR1 STD definition in the GEO block

        # Map coordinates to Sonnets ULC system
        xcoord, ycoord = self.mapPoint(xcoord, ycoord)

        dictParams = ({"ipolygon": None,
                       "ivertex": None,
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

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()
            [ipolygon, ivertex] = [dictParams["ipolygon"], dictParams["ivertex"]]

            # If the user does not specify ipolygon and ivertex, we must look through
            # the polygons that make up the circuit, and find the right values that
            # correspond to the position (xcoord, ycoord) specified by the user
            if ipolygon == None or ivertex == None:
                ilist = []
                numIndex = -1
                for index, line in enumerate(contents):
                    if line == "END GEO\n":
                        break
                    if line.split()[0] == "NUM":
                        numIndex = index
                        npoly = int(contents[numIndex].split()[1])
                        break
                if numIndex == -1:
                    raise self._exception("Cannot find NUM")

                # Start at the NUM definition and loop over polygons
                index = numIndex
                for poly in range(npoly):
                    # Jump to the line with nvertices and debugid entries, i.e.
                    # the next line with a least 5 entries
                    while len(contents[index].split()) < 5:
                        index += 1
                    nvertices = int(contents[index].split()[1])
                    ipolygon = int(contents[index].split()[4]) # debugid = ipolygon
                    # Jump to the first xvertex and yvertex
                    while len(contents[index].split()) != 2:
                        index += 1
                    # Look through list of vertices for vertices for which
                    # (xcoord,ycoord) lies between the vertex and the next
                    startindex = index
                    for index in range(startindex, startindex + nvertices - 1):
                        x0 = float(contents[index].split()[0])
                        y0 = float(contents[index].split()[1])
                        x1 = float(contents[index+1].split()[0])
                        y1 = float(contents[index+1].split()[1])
                        if min(x0,x1) <= xcoord and xcoord <= max(x0,x1) \
                            and min(y0,y1) <= ycoord and ycoord <= max(y0,y1):
                            # Criteria met: save polygon and vertex indices
                            ilist.append([ipolygon, index - startindex])

            # If ipolygon and ivertex are specified by the user use those values
            # (only necessary if the above code fails to find the correct values)
            else:
                ilist = [ipolygon, ivertex]

            # Look through the list of possible ipolygon and ivertex values
            if len(ilist) == 0:
                print("Cannot not add port: Attachment point ({:f},{:f}) does not lie on a polygon edge".format(xcoord, ycoord))
                raise self._exception("Could not add port")
            elif len(ilist) == 1:
                ipolygon, ivertex = ilist[0]
            elif len(ilist) > 2 and specify_polygon == False:
                ipolygon, ivertex = ilist[0]
            else:
                print("Cannot not add port: Several polygons to attach to")
                print("List of possible [ipolygon, ivertex]:")
                for i, line in enumerate(ilist):
                    print(ilist[i])
                print("Please specify ipolygon and ivertex when you call addPort")
                raise self._exception("Cannot not add port")

            # Now add the final ipolygon and ivertex values to the dictionary
            [dictParams["ipolygon"], dictParams["ivertex"]] = [ipolygon, ivertex]

            # Find the line that begins with GEO and add insertStr as the next line
            geoIndex = -1
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "GEO":
                    geoIndex = index
                    break
            if geoIndex == -1:
                raise self._exception("Cannot not find GEO")

            # Add port definition in the GEO block
            insertStr = ("POR1 STD\nPOLY {ipolygon} 1\n{ivertex}\n{portnum} {resist} {react} {induct} {capac} {:f} {:f}\n".format(xcoord, ycoord, **dictParams))
            contents.insert(geoIndex + 1, insertStr)
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def addComponent(self, x1, y1, x2, y2, level=0, type="ind", value=10, **kwargs):
        # Adds a SMD definition of TYPE IDEAL in the GEO block (after LORGN)
        # The component type is "ind" for inductor, "cap" for capacitor, or
        # "res" for resistor (or some of their aliases, see below)
        # The value argument sets the inductance/capacitance/resistance
        # The level argument sets the level at which the component is placed
        # The component's endpoints are (x1,y1) and (x2,y2) relative to lower left corner
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
        # Note: all positions are relative to upper left corner
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
            raise self._exception("Component neither vertical or horizontal!")

        # Extend the dictionary with more parameters
        dictParams.update({"smdp1_orientation": smdp1_orientation,
                           "smdp2_orientation": smdp2_orientation,
                           "leftpos": leftpos,
                           "rightpos": rightpos,
                           "toppos": toppos,
                           "bottompos": bottompos,
                           "xpos": xpos,
                           "ypos": ypos,
                           "levelnum": level,
                           "smdp1_levelnum": level,
                           "smdp2_levelnum": level,
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
        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            lorgnIndex = -1
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
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

    ########################################################################
    # POLYGONS                                                             #
    ########################################################################
    # Polygons defined in NUM in the GEO block.

    def shiftPolygons(self, xshift, yshift):
        # Shifts the positions of all polygons by (xshift, yshift)
        # with respect to LLC

        # Map coordinates to Sonnets ULC system
        xshift, yshift = self.mapPoint(xshift, yshift)

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            numIndex = -1
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "NUM":
                    numIndex = index
                    npoly = int(contents[numIndex].split()[1])
                    break
            if numIndex == -1:
                raise self._exception("Cannot find NUM")

            # Start at the NUM definition and loop over polygons
            index = numIndex
            for poly in range(npoly):
                # Jump to the line with nvertices (i.e. with a least 5 entries)
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

    ########################################################################
    # DIELECTRIC LAYERS (encloses the technology layers)                   #
    ########################################################################
    # The lines preceeding the first line of the BOX definition in the GEO
    # block. Anisotropy of the dielectric in the Z direction is not supported.

    def getNumberOfDielectricLayers(self):
        # Returns the number of layers in the BOX definition
        numberOfLayers = 0

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()
            # Find the BOX definition and count the number of preceeding lines
            # that start with a space (" "), each defining a dielectric layer
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "BOX":
                    while contents[index + 1][0] == " ":
                        numberOfLayers += 1
                        index += 1
                    break

        return numberOfLayers

    def addDielectricLayer(self, layer="top", **kwargs):
        # Add a dielectric layer to BOX in the GEO block with parameters in kwargs
        # Layers are indexed from 0 (= "top"), 1, 2 ect. to some max value (= "bottom")
        # The layer value refers to the layer number after the addition

        dictParams = ({"thickness": 0,
                       "erel": 1,
                       "mrel": 1,
                       "eloss": 0,
                       "mloss": 0,
                       "esignma": 0,
                       "nzpart": 0,
                       "name": "Unnamed"})

        # Update parameters with the user's input
        for key in kwargs.keys():
            if key not in dictParams:
                raise self._exception("Invalid argument: {:s}".format(key))
        dictParams.update(kwargs)

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            layerIndex = []
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "BOX":
                    layerIndex.append(index) # first entry is BOX index
                    index += 1
                    while contents[index][0] == " ":
                        layerIndex.append(index) # next entries are layers
                        index += 1
                    break
            if len(layerIndex) == 0:
                raise self._exception("Cannot not find BOX")

            # Convert special inputs to corresponding numeral
            if layer == "bottom" or layer >= len(layerIndex):
                layer = len(layerIndex) - 1
            elif layer == "top":
                layer = 0

            # Add the new dielectric layer as a new line in the appropriate order
            insertStr = ("      {thickness} {erel} {mrel} {eloss} {mloss} {esignma} {nzpart} \"{name}\"\n".format(**dictParams))
            contents.insert(layerIndex[layer] + 1, insertStr)
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def removeDielectricLayer(self, layer="top"):
        # Remove a dielectric layer from BOX in the GEO block
        # Layers are indexed from 0 (= "top"), 1, 2 ect. to some max value (= "bottom")

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Get the number of layers and the line index of the first layer
            # by the same method as in getNumberOfLayers()
            layerIndex = []
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "BOX":
                    layerIndex.append(index) # first entry is BOX index
                    index += 1
                    while contents[index][0] == " ":
                        layerIndex.append(index) # next entries are layers
                        index += 1
                    break
            if len(layerIndex) < 2:
                raise self._exception("Cannot not find layers")

            # Convert special inputs to corresponding numeral
            if layer == "bottom" or layer >= len(layerIndex) - 1:
                layer = len(layerIndex) - 2
            elif layer == "top":
                layer = 0

            # Remove the appropriate line and write to file
            contents.pop(layerIndex[layer] + 1)
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def setDielectricLayer(self, layer="top", **kwargs):
        # Set the parameters in a dielectric layer to the value specified by the user
        # Layers are indexed from 0 (= "top"), 1, 2 ect. to some max value (= "bottom")
        # Valid keyword arguments are defined in dictParams below

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            layerIndex = []
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "BOX":
                    layerIndex.append(index) # first entry is BOX index
                    index += 1
                    while contents[index][0] == " ":
                        layerIndex.append(index) # next entries are layers
                        index += 1
                    break
            if len(layerIndex) == 0:
                raise self._exception("Cannot not find layers")

            # Convert special inputs to corresponding numeral
            if layer == "bottom" or layer >= len(layerIndex) - 1:
                layer = len(layerIndex) - 2
            elif layer == "top":
                layer = 0

            # Grab old parameters
            params = contents[layerIndex[layer] + 1].split()

            # Sanity check
            if len(params) < 8:
                raise self._exception("Invalid dielectric layer definition")

            # Create dictionary with the old parameter values
            dictParams = ({"thickness": params[0],
                           "erel": params[1],
                           "mrel": params[2],
                           "eloss": params[3],
                           "mloss": params[4],
                           "esignma": params[5],
                           "nzpart": params[6],
                           "name": " ".join(params[7:])}) # list -> string with spaces

            # Update parameters with the user's input
            for key in kwargs.keys():
                if key not in dictParams:
                    raise self._exception("Invalid argument: {:s}".format(key))
            dictParams.update(kwargs)

            # Write the modified dielectric layer to the file
            insertStr = ("      {thickness} {erel} {mrel} {eloss} {mloss} {esignma} {nzpart} \"{name}\"\n".format(**dictParams))
            contents[layerIndex[layer] + 1] = insertStr
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    ########################################################################
    # TECHNOLOGY LAYERS (enclosed by dielectric layers)                    #
    ########################################################################
    # TECHLAY in the GEO block.

    def getNumberOfTechLayers(self, type="all"):
        # Returns the number of technology layers of the specified type
        # where type can be "metal", "via", "brick" or "all" (counts all)
        numberOfLayers = 0

        if type not in ["all", "metal", "via", "brick"]:
            raise self._exception("Invalid technology layer type: {:s}".format(type))

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()
            # Count all the TECHLAY definitions
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "TECHLAY":
                    if type == "all":
                        numberOfLayers += 1
                    elif type == "metal" and line.split()[1] == "METAL":
                        numberOfLayers += 1
                    elif type == "via" and line.split()[1] == "VIA":
                        numberOfLayers += 1
                    elif type == "brick" and line.split()[1] == "BRICK":
                        numberOfLayers += 1

        return numberOfLayers

    def setTechLayer(self, type="metal", layer="top", **kwargs):
        # Set the parameters in a technology layer to the value specified as kwargs
        # The layer is specified by its type (type = "metal", "via" or "brick")
        # and, if there are several layers of the same type, also by layer
        # Layers are indexed from 0 (= "top"), 1, 2 ect. to some max value (= "bottom")
        # Notice that this level indexing is reversed compared to Sonnet's ilevel
        # where ilevel = 0 is the bottom layer
        # Valid keyword arguments are defined in dictParams below

        if type not in ["metal", "via", "brick"]:
            raise self._exception("Invalid type: {:s}".format(type))

        # Default values for all parameters for any type (METAL, VIA or BRICK)
        dictParams = ({"lay_type": None,
                       "lay_name": None,
                       "mapping": None,
                       "type": None, # do not change (found from lay_type)
                       "ilevel": None,
                       "nvertices": None,
                       "mtype": None,
                       "filltype": None,
                       "debugid": None,
                       "xmin": None,
                       "ymin": None,
                       "xmax": None,
                       "ymax": None,
                       "conmax": None,
                       "res1": None, # do not change
                       "res2": None, # do not change
                       "edgemesh": None,
                       "to_level": 1,
                       "meshingfill": "RING",
                       "pads": "NOCOVERS"})

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Make a list of line indices and ilevels of all technology
            # layers of the type specified by the user
            layerIndex = []
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "TECHLAY":

                    # Search for a layer of the specified type
                    if type == "metal" and line.split()[1] == "METAL":
                        # Handle the optional "type" line and get level=ilevel
                        if len(contents[index + 1].split()) == 2:
                            level = contents[index + 2].split()[0]
                        else:
                            level = contents[index + 1].split()[0]
                        layerIndex.append([index, level])

                    if type == "via" and line.split()[1] == "VIA":
                        if len(contents[index + 1].split()) == 2:
                            level = contents[index + 2].split()[0]
                        else:
                            level = contents[index + 1].split()[0]
                        layerIndex.append([index, level])

                    if type == "brick" and line.split()[1] == "BRICK":
                        if len(contents[index + 1].split()) == 2:
                            level = contents[index + 2].split()[0]
                        else:
                            level = contents[index + 1].split()[0]
                        layerIndex.append([index, level])

            if len(layerIndex) == 0:
                raise self._exception("Cannot find layer")

            # If there is only one technology layer of the right type
            # there is no ambiguity (and no need to give the layer argument)
            elif len(layerIndex) == 1:
                layerBeginIndex = layerIndex[0][0]

            # Otherwise we need to find the layer based on the layer argument
            elif len(layerIndex) > 1:
                if layer == "bottom" or layer >= len(layerIndex):
                    layer = len(layerIndex) - 1
                elif layer == "top":
                    layer = 0

                # Translate layer = 0, 1, 2,... to a level and then a line index
                # Remember that smaller levels corresponds to lower levels, which
                # is opposite to the value of layer, where layer = 0 is top
                levels = [layerIndex[index][1] for index in range(len(layerIndex))]
                levels_sorted = levels
                levels_sorted.sort()
                level = levels_sorted[len(levels) - 1 - layer]
                layerBeginIndex = layerIndex[levels.index(level)][0]

            # Grab old parameters from file and update the default dictionary
            # We read one line at a time and update the dictionary

            # The first line (containing TECHLAY)
            currentIndex = layerBeginIndex
            currentLine = contents[currentIndex].split()
            dictParams["lay_type"] = currentLine[1]
            dictParams["lay_name"] = currentLine[2]
            dictParams["mapping"] = " ".join(currentLine[3:]) # string with spaces

            # The next line is optional, omission means type = MET POL
            currentIndex += 1
            currentLine = contents[currentIndex].split()
            if currentLine[0] in ["MET", "VIA", "BRI"]:
                dictParams["type"] = " ".join(currentLine)
                currentIndex += 1
            else:
                dictParams["type"] = "MET POL"

            # The next line has many parameters
            currentLine = contents[currentIndex].split()
            dictParamsFromFile = ({"ilevel": currentLine[0],
                                   "nvertices": currentLine[1],
                                   "mtype": currentLine[2],
                                   "filltype": currentLine[3],
                                   "debugid": currentLine[4],
                                   "xmin": currentLine[5],
                                   "ymin": currentLine[6],
                                   "xmax": currentLine[7],
                                   "ymax": currentLine[8],
                                   "conmax": currentLine[9],
                                   "res1": currentLine[10],
                                   "res2": currentLine[11],
                                   "edgemesh": currentLine[12]})
            dictParams.update(dictParamsFromFile)

            # The last line is only present for vias
            if dictParams["lay_type"] == "VIA":
                currentIndex += 1
                currentLine = contents[currentIndex].split()
                dictParams["to_level"] = currentLine[1]
                dictParams["meshingfill"] = currentLine[2]
                dictParams["pads"] = currentLine[3]

            # Sanity check
            if contents[currentIndex + 1] != "END\n":
                raise self._exception("Invalid TECHLAY defintion. Expected \"END\", but got: {:s}".format(contents[currentIndex + 1]))

            # Update the dictionary with the user's input to final dictionary
            for key in kwargs.keys():
                if key not in dictParams:
                    raise self._exception("Invalid argument: {:s}".format(key))
            dictParams.update(kwargs)

            # Sanity checks
            if dictParams["meshingfill"] not in ["RING", "CENTER", "VERTICES", "SOLID", "BAR"]:
                raise self._exception("Invalid meshingfill: {:s}".format(dictParams["meshingfill"]))
            if dictParams["pads"] not in ["NOCOVERS", "COVERS"]:
                raise self._exception("Invalid pads: {:s}".format(dictParams["pads"]))

            # Set the type according to the layer type, and convert lay_type
            # to caps if the user input was not in capitalized
            if dictParams["lay_type"] in ["METAL", "metal"]:
                dictParams["type"] = "MET POL"
                dictParams["lay_type"] = "METAL"
            elif dictParams["lay_type"] in ["VIA", "via"]:
                dictParams["type"] = "VIA POLYGON"
                dictParams["lay_type"] = "VIA"
            elif dictParams["lay_type"] in ["BRICK", "brick"]:
                dictParams["type"] = "BRI POL"
                dictParams["lay_type"] = "BRICK"
            else:
                raise self._exception("Invalid technology layer type: {:s}".format(dictParams["lay_type"]))

            # We have now saved all the data we need to define the modified
            # technology layer, so we can erase the old definition from the file
            # (this is useful because we can erase all lines from the first to
            # the END statement without thinking about the exact number of lines
            # which varies between technology layer definitions)
            currentIndex = layerBeginIndex
            while contents[currentIndex] != "END\n":
                contents.pop(currentIndex)

            # Write the lines that appear regardless of type to the file
            contents.insert(layerBeginIndex, "TECHLAY {lay_type} {lay_name} {mapping}\n".format(**dictParams))
            contents.insert(layerBeginIndex + 1, "{type}\n".format(**dictParams))
            contents.insert(layerBeginIndex + 2, "{ilevel} {nvertices} {mtype} {filltype} {debugid} {xmin} {ymin} {xmax} {ymax} {conmax} {res1} {res2} {edgemesh}\n".format(**dictParams))

            # Only for vias do we need to add an extra line
            if dictParams["lay_type"] == "VIA":
                contents.insert(layerBeginIndex + 3, "TOLEVEL {to_level} {meshingfill} {pads}\n".format(**dictParams))

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()


    '''
    def setTechLayer(self, type="metal", layer="top", **kwargs):
        # Set the parameters in a technology layer to the value specified as kwargs
        # The layer is specified by its type (type = "metal", "via" or "brick")
        # and, if there are several layers of the same type, also by layer
        # Layers are indexed from 0 (= "top"), 1, 2 ect. to some max value (= "bottom")
        # Notice that this level indexing is reversed compared to Sonnet's ilevel
        # where ilevel = 0 is the bottom layer
        # Valid keyword arguments are defined in dictParams below

        if type not in ["metal", "via", "brick"]:
            raise self._exception("Invalid type: {:s}".format(type))

        # Default values for all parameters for any type (METAL, VIA or BRICK)
        dictParams = ({"lay_type": None,
                       "lay_name": None,
                       "mapping": None,
                       "type": None, # do not change (found from lay_type)
                       "ilevel": None,
                       "nvertices": None,
                       "mtype": None,
                       "filltype": None,
                       "debugid": None,
                       "xmin": None,
                       "ymin": None,
                       "xmax": None,
                       "ymax": None,
                       "conmax": None,
                       "res1": None, # do not change
                       "res2": None, # do not change
                       "edgemesh": None,
                       "to_level": 1,
                       "meshingfill": "RING",
                       "pads": "NOCOVERS"})

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Make a list of line indices and ilevels of all technology
            # layers of the type specified by the user
            layerIndex = []
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "TECHLAY":

                    # Search for a layer of the specified type
                    if type == "metal" and line.split()[1] == "METAL":
                        # Handle the optional "type" line and get level=ilevel
                        if len(contents[index + 1].split()) == 2:
                            level = contents[index + 2].split()[0]
                        else:
                            level = contents[index + 1].split()[0]
                        layerIndex.append([index, level])

                    if type == "via" and line.split()[1] == "VIA":
                        if len(contents[index + 1].split()) == 2:
                            level = contents[index + 2].split()[0]
                        else:
                            level = contents[index + 1].split()[0]
                        layerIndex.append([index, level])

                    if type == "brick" and line.split()[1] == "BRICK":
                        if len(contents[index + 1].split()) == 2:
                            level = contents[index + 2].split()[0]
                        else:
                            level = contents[index + 1].split()[0]
                        layerIndex.append([index, level])

            if len(layerIndex) == 0:
                raise self._exception("Cannot find layer")

            # If there is only one technology layer of the right type
            # there is no ambiguity (and no need to give the layer argument)
            elif len(layerIndex) == 1:
                layerBeginIndex = layerIndex[0][0]

            # Otherwise we need to find the layer based on the layer argument
            elif len(layerIndex) > 1:
                if layer == "bottom" or layer >= len(layerIndex):
                    layer = len(layerIndex) - 1
                elif layer == "top":
                    layer = 0

                # Translate layer = 0, 1, 2,... to a level and then a line index
                # Remember that smaller levels corresponds to lower levels, which
                # is opposite to the value of layer, where layer = 0 is top
                levels = [layerIndex[index][1] for index in range(len(layerIndex))]
                levels_sorted = levels
                levels_sorted.sort()
                level = levels_sorted[len(levels) - 1 - layer]
                layerBeginIndex = layerIndex[levels.index(level)][0]

            # Grab old parameters from file and update the default dictionary
            # We read one line at a time and update the dictionary

            # The first line (containing TECHLAY)
            currentIndex = layerBeginIndex
            currentLine = contents[currentIndex].split()
            dictParams["lay_type"] = currentLine[1]
            dictParams["lay_name"] = currentLine[2]
            dictParams["mapping"] = " ".join(currentLine[3:]) # string with spaces

            # The next line is optional, omission means type = MET POL
            currentIndex += 1
            currentLine = contents[currentIndex].split()
            if currentLine[0] in ["MET", "VIA", "BRI"]:
                dictParams["type"] = " ".join(currentLine)
                currentIndex += 1
            else:
                dictParams["type"] = "MET POL"

            # The next line has many parameters
            currentLine = contents[currentIndex].split()
            dictParamsFromFile = ({"ilevel": currentLine[0],
                                   "nvertices": currentLine[1],
                                   "mtype": currentLine[2],
                                   "filltype": currentLine[3],
                                   "debugid": currentLine[4],
                                   "xmin": currentLine[5],
                                   "ymin": currentLine[6],
                                   "xmax": currentLine[7],
                                   "ymax": currentLine[8],
                                   "conmax": currentLine[9],
                                   "res1": currentLine[10],
                                   "res2": currentLine[11],
                                   "edgemesh": currentLine[12]})
            dictParams.update(dictParamsFromFile)

            # The last line is only present for vias
            if dictParams["lay_type"] == "VIA":
                currentIndex += 1
                currentLine = contents[currentIndex].split()
                dictParams["to_level"] = currentLine[1]
                dictParams["meshingfill"] = currentLine[2]
                dictParams["pads"] = currentLine[3]

            # Sanity check
            if contents[currentIndex + 1] != "END\n":
                raise self._exception("Invalid TECHLAY defintion. Expected \"END\", but got: {:s}".format(contents[currentIndex + 1]))

            # Update the dictionary with the user's input to final dictionary
            for key in kwargs.keys():
                if key not in dictParams:
                    raise self._exception("Invalid argument: {:s}".format(key))
            dictParams.update(kwargs)

            # Sanity checks
            if dictParams["meshingfill"] not in ["RING", "CENTER", "VERTICES", "SOLID", "BAR"]:
                raise self._exception("Invalid meshingfill: {:s}".format(dictParams["meshingfill"]))
            if dictParams["pads"] not in ["NOCOVERS", "COVERS"]:
                raise self._exception("Invalid pads: {:s}".format(dictParams["pads"]))

            # Set the type according to the layer type, and convert lay_type
            # to caps if the user input was not in capitalized
            if dictParams["lay_type"] in ["METAL", "metal"]:
                dictParams["type"] = "MET POL"
                dictParams["lay_type"] = "METAL"
            elif dictParams["lay_type"] in ["VIA", "via"]:
                dictParams["type"] = "VIA POLYGON"
                dictParams["lay_type"] = "VIA"
            elif dictParams["lay_type"] in ["BRICK", "brick"]:
                dictParams["type"] = "BRI POL"
                dictParams["lay_type"] = "BRICK"
            else:
                raise self._exception("Invalid technology layer type: {:s}".format(dictParams["lay_type"]))

            # We have now saved all the data we need to define the modified
            # technology layer, so we can erase the old definition from the file
            # (this is useful because we can erase all lines from the first to
            # the END statement without thinking about the exact number of lines
            # which varies between technology layer definitions)
            currentIndex = layerBeginIndex
            while contents[currentIndex] != "END\n":
                contents.pop(currentIndex)

            # Write the lines that appear regardless of type to the file
            contents.insert(layerBeginIndex, "TECHLAY {lay_type} {lay_name} {mapping}\n".format(**dictParams))
            contents.insert(layerBeginIndex + 1, "{type}\n".format(**dictParams))
            contents.insert(layerBeginIndex + 2, "{ilevel} {nvertices} {mtype} {filltype} {debugid} {xmin} {ymin} {xmax} {ymax} {conmax} {res1} {res2} {edgemesh}\n".format(**dictParams))

            # Only for vias do we need to add an extra line
            if dictParams["lay_type"] == "VIA":
                contents.insert(layerBeginIndex + 3, "TOLEVEL {to_level} {meshingfill} {pads}\n".format(**dictParams))

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()
    '''

    ########################################################################
    # BOX (dimensions and parameters of the enclosed substrates)           #
    ########################################################################
    # First line in the BOX definition in the GEO block.

    def setBox(self, **kwargs):
        # Set the parameters of the BOX to the values specified in kwargs
        # Valid keyword arguments are defined in dictParams below

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            boxIndex = -1
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                if line.split()[0] == "BOX":
                    boxIndex = index
                    break
            if boxIndex == -1:
                raise self._exception("Cannot not find BOX")

            # Grab old parameters
            params = contents[boxIndex].split()

            # Sanity check
            if len(params) < 6:
                raise self._exception("Invalid BOX definition")

            # Create dictionary with the old parameter values
            dictParams = ({"nlev": params[1],
                           "xwidth": params[2],
                           "ywidth": params[3],
                           "xcells2": params[4],
                           "ycells2": params[5],
                           "nsubs": params[6], # do not change
                           "eeff": params[7]})

            # Update parameters with the user's input
            for key in kwargs.keys():
                if key not in dictParams:
                    raise self._exception("Invalid argument: {:s}".format(key))
            dictParams.update(kwargs)

            # Write the modified BOX definition to the file
            insertStr = ("BOX {nlev} {xwidth} {ywidth} {xcells2} {ycells2} {nsubs} {eeff}\n".format(**dictParams))
            contents[boxIndex] = insertStr
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def cropBox(self, xcellsize=1, ycellsize=1):
        # Crops the BOX to the circuit and set the cellsize in x and y direction and
        # sets the local origin (LORGN in GEO block) in order to place point correctly
        # If the circuit is rectangular, this ensures that ports added to the
        # edges of the circuit is also at the edge of the BOX, which is required

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Get BOX dimensions (xwidth, ywidth) and LORGN and NUM indices
            boxIndex = -1
            lorgnIndex = -1
            numIndex = -1
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                elif line.split()[0] == "BOX":
                    boxIndex = index
                    params = contents[boxIndex].split()
                    if len(params) < 6:
                        raise self._exception("Invalid BOX definition")
                    xwidth, ywidth = float(params[2]), float(params[3])
                elif line.split()[0] == "LORGN":
                    lorgnIndex = index
                elif line.split()[0] == "NUM":
                    numIndex = index
                    npoly = int(contents[numIndex].split()[1])

            if boxIndex == -1:
                raise self._exception("Cannot find BOX")
            if lorgnIndex == -1:
                raise self._exception("Cannot find LORGN")
            if numIndex == -1:
                raise self._exception("Cannot find NUM")

            # Start at the NUM definition and loop over polygons
            index = numIndex
            xlist = []
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
                    xlist.append(float(coordinates[0]))
                    ylist.append(float(coordinates[1]))

            # Get circuit dimensions and redefine the local origin (LORGN)
            xmin, ymin, xmax, ymax = min(xlist), min(ylist), max(xlist), max(ylist)
            contents[lorgnIndex] = "LORGN {:f} {:f} U\n".format(0, ymax-ymin)
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

        # Shift the circuit
        self.shiftPorts(-xmin, 2*ymin - ymax)
        self.shiftComponents(-xmin, 2*ymin - ymax)
        self.shiftPolygons(-xmin, 2*ymin - ymax)

        # Resize BOX with the circuit's dimensions
        self.setBox(xwidth = xmax - xmin, ywidth = ymax - ymin, \
            xcells2 = int(2*(xmax - xmin)/xcellsize), \
            ycells2 = int(2*(ymax - ymin)/ycellsize))

    ########################################################################
    # FREQUENCY SWEEPS (frequencies used for simulation)                   #
    ########################################################################
    # The FREQ block contains the frequency sweeps which have been input in
    # a project. Which sweep is being used is set in the CONTROL block.
    # The default frequency unit is GHz, set in the DIM block.

    def setFreq(self, f1=5, f2=8, fstep=None):
        # Redefines or adds the FREQ block with a single frequency sweep, and
        # sets this sweep as the current sweep in the CONTROL block
        # Adds the CONTROL block with some standard setting if it does not exist
        # Currently, the following sweep types are implemented:
        # SIMPLE: Linear sweep from f1 to f2 in steps fstep if fstep is speficied
        # ABS: Adaptive sweep from f1 to f2 if fstep is left unspecified (None)

        if fstep == None:
            sweepType = "ABS"
            insertStr = "ABS {:f} {:f}\n".format(f1, f2)
        elif fstep >= 0:
            sweepType = "SIMPLE"
            insertStr = "SIMPLE {:f} {:f} {:f}\n".format(f1, f2, fstep)
        else:
            raise self._exception("Invalid frequency sweep definition")

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()

            # Update the FREQ block if it exists
            freqExists = False
            for index, line in enumerate(contents):
                if line == "FREQ\n":
                    freqExists = True
                    contents.insert(index + 1, insertStr)
                    print("FREQ found") # DEBUGGING
                    while "END FREQ\n" != contents[index + 2]:
                        contents.pop(index + 2)
                    break

            # Add the FREQ block after the DIM block if it does not exists
            if freqExists == False:
                for index, line in enumerate(contents):
                    if line == "END DIM\n":
                        contents.insert(index + 1, "FREQ\n")
                        contents.insert(index + 2, insertStr)
                        contents.insert(index + 3, "END FREQ\n")
                        break

            # Overwrite any previously set sweep if the CONTROL exists
            controlExists = False
            for index, line in enumerate(contents):
                if line == "CONTROL\n":
                    controlExists = True
                    contents.insert(index + 1, sweepType + "\n")
                    index += 2
                    while "END CONTROL\n" != contents[index]:
                        if contents[index].split()[0] in ["SIMPLE", "STD", "ABS"]:
                            contents.pop(index)
                        index += 1
                    break

            # Create the CONTROL block after the FREQ block with some default
            # settings if it does not exist
            if controlExists == False:
                insertStr = "CONTROL\n" + sweepType + "\nOPTIONS -d\nSPEED 1\nCACHE_ABS 1\nTARG_ABS 300\nQ_ACC N\nEND CONTROL\n"
                for index, line in enumerate(contents):
                    print("{:d}: {:s}".format(index, line))
                    if line == "END FREQ\n":
                        print("END FREQ found")
                        contents.insert(index + 1, insertStr)
                        break

            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()


    ########################################################################
    # MISCELLANEOUS FUNCTIONS                                              #
    ########################################################################

    def addComment(self, string):
        # Add string as a comment at the top of the Sonnet project file
        # Comments in Sonnet project files start with "!"

        with open(self._sonnet_file_path+self._sonnet_file, 'r+') as fd:
            contents = fd.readlines()
            contents.insert(0, "! " + string + "\n")
            fd.seek(0)
            fd.writelines(contents)
            fd.truncate()

    def mapPoint(self, xcoord, ycoord):
        # Sonnet computes points relative to the circuit's upper left corner (ULC),
        # but it's easier for the user to specify points relative to the lower
        # left corner (LLC). This function takes an input point (xcoord, ycoord)
        # from the user's LLC and returns the point in Sonnet's ULC system

        with open(self._sonnet_file_path+self._sonnet_file, 'r') as fd:
            contents = fd.readlines()

            # Get the NUM index
            numIndex = -1
            for index, line in enumerate(contents):
                if line == "END GEO\n":
                    break
                elif line.split()[0] == "NUM":
                    numIndex = index
                    npoly = int(contents[numIndex].split()[1])

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
        # Add comment
        self.addComment("The EQuS custom Sonnet makeover has been performed")
        # Set number of metalization levels to 1 (a standard microchip)
        self.setBox(nlev=1)
        # Remove top dielectric layer (such that there is two left)
        self.removeDielectricLayer()
        # Set the parameters in the bottom dielectric layer appropriate for Silicon
        self.setDielectricLayer("bottom", thickness=279, erel=11.9, eloss=1e-6, name="Silicon (intrinsic)")
        # Set the parameters in the top dielectric layer appropriate for Vacuum
        self.setDielectricLayer("top", thickness=3000, name="Vacuum")
        # Set the technology layer to lossless metal (mtype=-1), conformal meshing (filltype="V")
        # and place it between the two dielectric layers (ilevel=0)
        self.setTechLayer(mtype=-1, filltype="V", ilevel=0)

'''
TO DO:
    Generalize runMakeover to suit any realistic situation
    Run emgraph.exe to extract data (what are the options? no help from -h, --h, -H, -help, -Help, -?)
    Clean up exceptions and error messages in code
    Clean up string formatting in code to comply with new style
    Use flake8 style to clean up code style & make documentation
    Support VIA and BRICK technology layers TECHLAY
        --> how does parameters in TECHLAY influence NUM?
        --> should the to_layer and ilevel options be more user friendly? (better default values?)
    Support VIA and BRICK polygons in NUM
    addPort: make it more userfriendly to pick other attachment points, for
        instance by specifying which layer to attach to (what will be used?)
    setFile/Filepath: / can be used instead of \\. Append / if the user forgets.
    runGdsTranslator: remove extra layers, extract actual layer from gds file like this:

        gdsfile = gdspy.GdsLibrary(infile='filename.gds')
        layers = []
        for k,v in gdsfile.cell_dict.items():
            layers.append(list(v.get_layers()))
        layers = np.array(layers).flatten()
        print(layers)

    removeDielectricLayer: nlev -> nlev-1 in BOX statement
    setDielectricLayer: ability to map a tech layer (specified by gds layer index)
        to the top of a dielectric layer (specify its index), like
        setDielectricLayer(techlayer=50, dielectriclayer=0 (=bottom))
    When simulating on a server, we should not monitor processes locally on the computer
    Map techlayer onto dielectric layer:  setTechLayerDielectric(techlayer = 23, dielectriclayer = 0)
        with techlayer index from gdspy
    Dictionary/list of techlayers (indexed by stream/gds) and dielectric layers (0,1,...)
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
