# -*- coding: utf-8 -*-

__license__ = 'GNU General Public License 3.0'
__docformat__ = 'reStructuredText'

import subprocess
import time
import os
import platform
OS = platform.system()

if OS == "Windows":
   from win32com.client import GetObject

class Project():
    # Only geometry projects are supported
    def __init__(self):
        self.preheader = None
        self.header = None
        self.dim = None
        self.geo = None
        self.control = None
        self.freq = None
        self.opt = None
        self.varswp = None
        self.fileout = None
        self.subdiv = None
        self.qsg = None

class Preheader():
    def __init__(self):
        self.lines = []

class Header():
    def __init__(self):
        self.lines = []

class Dim():
    def __init__(self):
        self.lines = []

class Geo():
    def __init__(self):
        self.tmet = None
        self.bmet = None
        self.met = None
        self.box = None
        self.bricks = []  # Stores list of brick materials
        self.dlayers = []
        self.valvars = []
        self.lorgn = None
        self.npoly = None

class Tmet():
    def __init__(self):
        self.name = "Lossless"
        self.patternid = 0
        self.type = "SUP"
        self.values = [0, 0, 0, 0]

class Bmet():
    def __init__(self):
        self.name = "Lossless"
        self.patternid = 0
        self.type = "SUP"
        self.values = [0, 0, 0, 0]

class Met():
    def __init__(self):
        self.name = "Lossless"
        self.patternid = 0
        self.type = "SUP"
        self.values = [0, 0, 0, 0]

class Brick():
    def __init__(self):
        self.name = "Air"
        self.patternid = 0
        self.values = [0, 0, 0]  # [Erel, Loss Tan, Cond] elements can be lists length 3 (isotropic) or length 9 (anisotropic)
        self.isIsotropic = True

class Box():
    def __init__(self):
        self.nlev = None
        self.xwidth = None
        self.ywidth = None
        self.xcells2 = None
        self.ycells2 = None
        self.nsubs = None
        self.eeff = None

class Dlayer():
    def __init__(self):
        self.ilevel = 0
        self.thickness = 0
        self.erel = 1
        self.mrel = 1
        self.eloss = 0
        self.mloss = 0
        self.esignma = 0
        self.nzpart = 0
        self.name = "New layer"
        # Stuff in the same layer
        self.tlayers = []
        self.ports = []
        self.components = []

class Tlayer():
    def __init__(self):
        self.lay_type = "METAL" # "METAL", "BRICK" or "VIA"
        self.lay_name = None
        self.dxf_layer = "<UNSPECIFIED>"
        self.gds_stream = None
        self.gds_object = None
        self.type = "MET POL" # "MET POL", "BRI POL" or "VIA POLYGON"
        self.ilevel = None
        self.nvertices = None
        self.mtype = -1
        self.filltype = "N"
        self.debugid = 0
        self.xmin = 1
        self.ymin = 1
        self.xmax = 100
        self.ymax = 100
        self.conmax = 0
        self.res1 = 0
        self.res2 = 0
        self.edgemesh = "Y"
        self.to_level = None
        self.meshingfill = "RING"
        self.pads = "NOCOVERS"
        # List of associated polygons
        self.polygons = []

class Polygon():
    def __init__(self):
        self.type = "MET POL" # "MET POL", "BRI POL" or "VIA POLYGON"
        self.ilevel = None
        self.nvertices = None
        self.mtype = -1
        self.filltype = "N"
        self.debugid = 0
        self.xmin = 1
        self.ymin = 1
        self.xmax = 100
        self.ymax = 100
        self.conmax = 0
        self.res1 = 0
        self.res2 = 0
        self.edgemesh = "Y"
        self.to_level = None
        self.meshingfill = "RING"
        self.pads = "NOCOVERS"
        self.gds_stream = None
        self.gds_object = None
        self.inherit = "INH"
        # List of [xvertex, yvertex]
        self.vertices = []

class Port():
    def __init__(self):
        self.type = "STD"
        self.ipolygon = None
        self.ivertex = None
        self.portnum = None
        self.resist = 50
        self.react = 0
        self.induct = 0
        self.capac = 0
        self.xcoord = None
        self.ycoord = None

class Component():
    # Only ideal components are implemeted
    def __init__(self):
        self.levelnum = None
        self.label = None
        self.objectid = None
        self.gndref = "F"
        self.twtype = "1CELL"
        self.leftpos = None
        self.rightpos = None
        self.toppos = None
        self.bottompos = None
        self.pbshw = "N"
        self.xpos = None
        self.ypos = None
        self.smdp1_levelnum = None
        self.smdp1_x = None
        self.smdp1_y = None
        self.smdp1_orientation = None
        self.smdp1_portnum = None
        self.smdp1_pinnum = 1 # unclear what pinnum is
        self.smdp2_levelnum = None
        self.smdp2_x = None
        self.smdp2_y = None
        self.smdp2_orientation = None
        self.smdp2_portnum = None
        self.smdp2_pinnum = 2 # unclear what pinnum is
        self.idealtype = "IND"
        self.compval = 30

class Valvar():
    def __init__(self):
        self.varname = None
        self.unittype = None
        self.value = 30
        self.description = ""

class Lorgn():
    def __init__(self):
        self.x = None
        self.y = None
        self.locked = "U"

class Control():
    def __init__(self):
        self.sweep = "ABS" # SIMPLE, ABS or VARSWP
        self.options = "-d"
        self.subsplam = None
        self.subsplam_subslambda = None
        self.edgecheck = None
        self.edgecheck_numlevels = None
        self.edgecheck_checktype = None
        self.cfmax = None
        self.cfmax_subfreq = None
        self.cepsy = None
        self.cepsy_epsilon = None
        self.filename = None
        self.speed = 1
        self.res_abs = None
        self.res_abs_resolution = None
        self.cache_abs = 1
        self.targ_abs = 300
        self.q_acc = "Y"
        self.det_abs_res = None

class Freq():
    # Only SIMPLE and ABS sweeps are implemeted
    def __init__(self):
        self.sweep = "ABS" # SIMPLE or ABS
        self.f1 = None
        self.f2 = None
        self.fstep = None

class Opt():
    def __init__(self):
        self.lines = []

class Varswp():
    def __init__(self):
        # List of Psweep instances
        self.psweeps = []

class Psweep():
    # Only SWEEP and ABS_ENTRY sweeps are implemeted
    def __init__(self):
        self.sweeptype = "ABS_ENTRY" # SWEEP or ABS_ENTRY
        self.f1 = 5
        self.f2 = 8
        self.fstep = None
        # List of Var instances
        self.vars = []

class Var():
    def __init__(self):
        self.parameter = None
        self.ytype = "Y" # "N" or any of the Ytypes
        self.min = None
        self.max = None
        self.step = None

class Fileout():
    # Only a single "Response" file (for geometry projects) is implemented
    def __init__(self):
        self.filetype = "CSV"
        self.embed = "D"
        self.abs_inc = "Y"
        self.filename = "$BASENAME.csv"
        self.comments = "NC"
        self.sig = 8
        self.partype = "S"
        self.parform = "DB"
        self.ports = "R 50"
        self.folder = None

class Subdiv():
    def __init__(self):
        self.lines = []

class Qsg():
    def __init__(self):
        self.lines = []

class sonnet(object):
    """
    Basic class for all interactions between Sonnet and Python, and for storing the Sonnet project. Start your interactions with SonPy by creating an instance of this class, like so:

        >>> import sonpy
        >>> snt = sonpy.sonnet()

    All the functions of SonPy described in this API documention are functions defined in the :class:`sonnet` class.
    """

    # Tested on Windows, can be extended to Linux (but not Mac)

    def __init__(self):
        # Settings for em simulator
        self.exception = Exception
        self.executable_path = "C:\\Program Files (x86)\\Sonnet Software\\14.54\\bin\\"
        self.executable_file = "em.exe"
        self.executable_and_monitor_file = "emstatus.exe"
        self.executable_and_monitor_options = "-Run"
        self.sonnet_file_path = "C:\\Users\\Lab\\Desktop\\sonnet_test\\"
        self.sonnet_file = "test.son"
        self.sonnet_options = "-v"
        self.done_flag = 1
        self.run_count = 0
        self.em_process = None
        self.emstatus_process = None
        self.parentPID = None
        self.emPID = None

        # Settings for the gds to son translator
        self.gds_translator_file = "gds.exe"
        self.gds_translator_options = "-v"
        self.gds_file_path = self.sonnet_file_path
        self.gds_file = "test.gds"
        self.gds_process = None

        # Settings for data extraction and plotting
        self.data_file = self.sonnet_file[:-3] + "csv"
        self.data_file_path = self.sonnet_file_path

        # Class containing the Sonnet project
        self.project = None

    def __del__(self):
        self.em_process = None
        self.emstatus_process = None
        self.project = None

    ########################################################################
    # SET FILEPATHS AND FILENAMES                                          #
    ########################################################################

    def setSonnetInstallationPath(self, path):
        """
        Sets the path of the Sonnet installation.

        :param str path: Path to Sonnet executables ``em.exe``, ``emstatus.exe`` and ``gds.exe``. Default is ``C:\\Program Files (x86)\\Sonnet Software\\14.54\\bin\\``.
        """
        self.executable_path = path
        if self.executable_path[-1] != '\\':
            self.executable_path += '\\'

    def setSonnetFile(self, filename):
        """
        Sets the filename of the Sonnet project file.

        :param str filename: Sonnet project file. Default is ``test.son``.
        """
        self.sonnet_file = filename

    def setSonnetFilePath(self, path):
        """
        Sets the path of the Sonnet project file.

        :param str path: Path to the Sonnet project file. Default is ``C:\\Users\\Lab\\Desktop\\sonnet_test\\``.
        """
        self.sonnet_file_path = path
        if self.sonnet_file_path[-1] != '\\':
            self.sonnet_file_path += '\\'

    def setGdsFile(self, filename):
        """
        Sets the filename of the GDSII file. It furthermore sets the Sonnet project file and data file to the same name (but with extensions .son and .csv, respectively).

        :param str filename: GDSII file. Default is ``test.gds``.

        """
        self.gds_file = filename
        # Also set Sonnet and data file name
        self.setSonnetFile(self.gds_file[:-3] + 'son')
        self.setDataFile(self.gds_file[:-3] + 'csv')

    def setGdsFilePath(self, path):
        """
        Sets the path of the GDSII file. It furthermore sets the paths to the Sonnet project file and data file to the same path.

        :param str path: Path to the GDSII file. Default is the Sonnet project path.

        :Example:
            Say you have ``myproject.gds`` that you want to use that as a starting point for a Sonnet project.

            >>> import os
            >>> snt.setGdsFilePath(os.getcwd()) # get current work directory
            >>> snt.setGdsFile('myproject.gds')

            SonPy will now associate ``myproject.son`` and ``myproject.csv`` (in the current directory) with the current project, even if these files do not exist yet.
        """
        self.gds_file_path = path
        if self.gds_file_path[-1] != '\\':
            self.gds_file_path += '\\'
        # Also set Sonnet and data file paths
        self.setSonnetFilePath(self.gds_file_path)
        self.setDataFilePath(self.gds_file_path)

    def setDataFile(self, filename):
        """
        Sets the filename of the data file.

        :param str filename: Data file. Default is the Sonnet project filename, but with the extension .csv instead of .son.
        """
        self.data_file = filename

    def setDataFilePath(self, path):
        """
        Sets the filepath of the data file.

        :param str path: Path to the data file. Default is the Sonnet project path.
        """
        self.data_file_path = path
        if self.data_file_path[-1] != '\\':
            self.data_file_path += '\\'

    ########################################################################
    # GDS TO SONNET PROJECT FILE TRANSLATOR (gds.exe)                      #
    ########################################################################

    def setTemplateFile(self, filename):
        """
        Sets an existing Sonnet project file (in the current directory) as template. When converting a GDSII file, the resulting Sonnet project file will inherit the settings of the template.

        :param str filename: Filename of the template Sonnet project file.
        """
        self.gds_translator_options = "-i{:s}".format(filename)

    def runGdsTranslator(self, silent=False):
        """
        Runs Sonnet's GDSII file to Sonnet project file translator. A Sonnet project file with the same name as the GDSII file is created in the same directory.

        After the translation process has run, the following functions are called:

        1. :func:`readProject()`: Reads the created Sonnet project file into SonPy.
        2. :func:`collapseDlayers()`: Removes empty dielectric layers.
        3. :func:`cropBox()`: Crops the bounding box to the edge of the circuit.

        :param bool silent: Toggle wait message.
        """

        # Verify gds file exists
        file_found = 0
        for root, dirs, files in os.walk(self.gds_file_path):
            for file in files:
                # Make search case insensitive
                if self.gds_file.lower() == file.lower():
                    file_found = 1

        if (file_found == 0):
            print("GDSII file {:s} cannot be located in path {:s}".format(self.gds_file, self.gds_file_path))
            raise self.exception("GDSII file not found! Check that directory and filename are correct")

        # Convert gds file to son file through Sonnet's gds.exe
        args = ([self.executable_path + self.gds_translator_file, # command
                 self.gds_translator_options, # options
                 self.gds_file_path + self.gds_file]) # file

        try:
            # Run conversion process
            self.gds_process = subprocess.Popen(args, stdout=subprocess.PIPE)

        except:
            print("Error! Cannot start process, use setSonnetInstallationPath(path) to point the class to the location of your gds.exe file")
            print("Current path is {:s}".format(self.executable_path))
            raise self.exception("Cannot run gds executable file, file not found")

        # Wait for the process to complete
        if silent == False:
            print('Translating...')
        self.gds_process.wait()

        # Read the Sonnet file into Sonpy and run some default changes
        self.readProject()
        self.collapseDlayers()
        self.cropBox()

    ########################################################################
    # READ AND WRITE THE SONNET PROJECT FILE                               #
    ########################################################################

    def readProject(self):
        """
        Reads the Sonnet project file into SonPy. This function is run in :func:`runGdsTranslator` to ensure the created Sonnet project file is read into SonPy for further manipulation.
        """

        # Initialize Sonnet project
        project = Project()
        self.project = project

        with open(self.sonnet_file_path + self.sonnet_file, 'r') as fd:

            line = fd.readline()
            preheader = Preheader()
            project.preheader = preheader
            while line != "HEADER\n":
                # Save all lines before HEADER block
                preheader.lines.append(line)
                line = fd.readline()

            while line != "":

                if line == "HEADER\n":
                    # Initialize HEADER block
                    header = Header()
                    project.header = header
                    line = fd.readline()

                    while line != "END HEADER\n":
                        # Save all lines
                        header.lines.append(line)
                        line = fd.readline()

                elif line == "DIM\n":
                    # Initialize DIM block
                    dim = Dim()
                    project.dim = dim
                    line = fd.readline()

                    while line != "END DIM\n":
                        # Save all lines
                        dim.lines.append(line)
                        line = fd.readline()

                elif line == "GEO\n":
                    # Initialize GEO block
                    geo = Geo()
                    dlayers = []
                    valvars = []
                    ports = []
                    geo.dlayers = dlayers
                    geo.valvars = valvars
                    project.geo = geo
                    line = fd.readline()

                    while line != "END GEO\n":

                        if line.split()[0] == "TMET":
                            # Initialize top metal
                            params = line.split()
                            tmet = Tmet()
                            tmet.name = params[1]  # assume no spaces
                            tmet.patternid = int(params[2])
                            tmet.type = params[3]
                            tmet.values = []
                            for params in params[4:]:
                                tmet.values.append(float(params))
                            geo.tmet = tmet
                            line = fd.readline()

                        elif line.split()[0] == "BMET":
                            # Initialize bottom metal
                            params = line.split()
                            bmet = Bmet()
                            bmet.name = params[1]  # assume no spaces
                            bmet.patternid = int(params[2])
                            bmet.type = params[3]
                            bmet.values = []
                            for params in params[4:]:
                                bmet.values.append(float(params))
                            geo.bmet = bmet
                            line = fd.readline()

                        elif line.split()[0] == "MET":
                            # Initialize metal
                            params = line.split()
                            met = Met()
                            met.name = params[1] # assume no spaces
                            met.patternid = int(params[2])
                            met.type = params[3]
                            met.values = []
                            for params in params[4:]:
                                met.values.append(float(params))
                            geo.met = met
                            line = fd.readline()

                        elif line.split()[0] == "BRI":
                            # Initialize isotropic brick material
                            params = line.split()
                            bri = Brick()
                            bri.name = params[1]  # assume no spaces
                            bri.patternid = int(params[2])
                            bri.isIsotropic = True
                            bri.values = []
                            for params in params[3:]:
                                bri.values.append(float(params))
                            geo.bricks.append(bri)
                            line = fd.readline()

                        elif line.split()[0] == "BRA":
                            # Initialize anisotropic brick material
                            params = line.split()
                            bri = Brick()
                            bri.name = params[1]  # assume no spaces
                            bri.patternid = int(params[2])
                            bri.isIsotropic = False
                            bri.values = []
                            for params in params[3:]:
                                bri.values.append(float(params))
                            geo.bricks.append(bri)
                            line = fd.readline()

                        elif line.split()[0] == "BOX":
                            # Initialize BOX
                            params = line.split()
                            box = Box()
                            box.nlev = int(params[1])
                            box.xwidth = float(params[2])
                            box.ywidth = float(params[3])
                            box.xcells2 = float(params[4])
                            box.ycells2 = float(params[5])
                            box.nsubs = int(params[6])
                            box.eeff = float(params[7])
                            geo.box = box
                            # Initialize dielectric layers
                            layerIndex = 0
                            line = fd.readline()
                            while line[0] == " ":
                                params = line.split()
                                dlayer = Dlayer()
                                dlayer.ilevel = layerIndex
                                dlayer.thickness = float(params[0])
                                dlayer.erel = float(params[1])
                                dlayer.mrel = float(params[2])
                                dlayer.eloss = float(params[3])
                                dlayer.mloss = float(params[4])
                                dlayer.esignma = float(params[5])
                                dlayer.nzpart = int(params[6])
                                dlayer.name = " ".join(params[7:]).replace('"','')
                                dlayers.append(dlayer)
                                layerIndex += 1
                                line = fd.readline()

                        elif line.split()[0] == "TECHLAY":
                            # Initialize technology layer and add it to dlayer
                            params = line.split()
                            tlayer = Tlayer()
                            tlayer.lay_type = params[1]
                            tlayer.lay_name = params[2]
                            tlayer.dxf_layer = params[3]
                            tlayer.gds_stream = int(params[4])
                            print(tlayer.gds_stream)
                            tlayer.gds_object = int(params[5])
                            params = fd.readline().split()
                            if len(params) != 13:
                                tlayer.type = " ".join(params)
                                params = fd.readline().split()
                            else:
                                tlayer.type = "MET POL"
                            tlayer.ilevel = int(params[0])
                            tlayer.nvertices = int(params[1])
                            tlayer.mtype = int(params[2])
                            tlayer.filltype = params[3]
                            tlayer.debugid = int(params[4])
                            tlayer.xmin = int(params[5])
                            tlayer.ymin = int(params[6])
                            tlayer.xmax = int(params[7])
                            tlayer.ymax = int(params[8])
                            tlayer.conmax = int(params[9])
                            tlayer.res1 = int(params[10])
                            tlayer.res2 = int(params[11])
                            tlayer.edgemesh = params[12]
                            line = fd.readline()
                            if line.split()[0] == "TOLEVEL":
                                params = line.split()
                                tlayer.to_level = int(params[1])
                                tlayer.meshingfill = params[2]
                                tlayer.pads = params[3]
                                line = fd.readline()
                            while line == "END\n":
                                line = fd.readline()
                            dlayers[tlayer.ilevel].tlayers.append(tlayer)

                        elif line.split()[0] == "VALVAR":
                            # Initialize variable parameter
                            params = line.split()
                            valvar = Valvar()
                            valvar.varname = params[1]
                            valvar.unittype = params[2]
                            valvar.value = float(params[3])
                            valvar.description = params[4].replace('"','')
                            valvars.append(valvar)
                            line = fd.readline()

                        elif line.split()[0] == "LORGN":
                            # Initialize location of origin
                            params = line.split()
                            lorgn = Lorgn()
                            lorgn.x = float(params[1])
                            lorgn.y = float(params[2])
                            lorgn.locked = params[3]
                            geo.lorgn = lorgn
                            line = fd.readline()

                        elif line.split()[0] == "POR1":
                            # Initialize port
                            port = Port()
                            port.type = line.split()[1]
                            port.ipolygon = int(fd.readline().split()[1])
                            port.ivertex = int(fd.readline().split()[0])
                            params = fd.readline().split()
                            port.portnum = int(params[0])
                            port.resist = float(params[1])
                            port.react = float(params[2])
                            port.induct = float(params[3])
                            port.capac = float(params[4])
                            port.xcoord = float(params[5])
                            port.ycoord = float(params[6])
                            # We can not yet assign port to dlayer because
                            # its location is hidden in ipolygon, so for now
                            # we save port in a list of ports
                            ports.append(port)
                            line = fd.readline()

                        elif line.split()[0] == "SMD":
                            # Initialize component and add it to dlayer
                            component = Component()
                            component.levelnum = int(line.split()[1])
                            component.label = line.split()[2].replace('"','')
                            component.objectid = int(fd.readline().split()[1])
                            component.gndref = fd.readline().split()[1]
                            component.twtype = fd.readline().split()[1]
                            sbox = fd.readline().split()
                            component.leftpos = float(sbox[1])
                            component.rightpos = float(sbox[2])
                            component.toppos = float(sbox[3])
                            component.bottompos = float(sbox[4])
                            component.pbshw = fd.readline().split()[1]
                            lpos = fd.readline().split()
                            component.xpos = float(lpos[1])
                            component.ypos = float(lpos[2])
                            typeideal = fd.readline().split()
                            component.idealtype = typeideal[2]
                            compval = typeideal[3]
                            # If compval is in quotes, it is a variable parameter
                            if compval[0] == '"' and compval[-1] == '"':
                                component.compval = compval.replace('"','')
                            # Otherwise it is a float value
                            else:
                                component.compval = float(compval)
                            smdp1 = fd.readline().split()
                            component.smdp1_levelnum = int(smdp1[1])
                            component.smdp1_x = float(smdp1[2])
                            component.smdp1_y = float(smdp1[3])
                            component.smdp1_orientation = smdp1[4]
                            component.smdp1_portnum = int(smdp1[5])
                            component.smdp1_pinnum = int(smdp1[6])
                            smdp2 = fd.readline().split()
                            component.smdp2_levelnum = int(smdp2[1])
                            component.smdp2_x = float(smdp2[2])
                            component.smdp2_y = float(smdp2[3])
                            component.smdp2_orientation = smdp2[4]
                            component.smdp2_portnum = int(smdp2[5])
                            component.smdp2_pinnum = int(smdp2[6])
                            dlayers[component.levelnum].components.append(component)
                            line = fd.readline()
                            line = fd.readline()

                        elif line.split()[0] == "NUM":
                            # Associate polygons with technology layers
                            npoly = int(line.split()[1])
                            geo.npoly = npoly
                            for poly in range(npoly):
                                polygon = Polygon()
                                params = fd.readline().split()
                                if len(params) != 13:
                                    polygon.type = " ".join(params)
                                    params = fd.readline().split()
                                else:
                                    polygon.type = "MET POL"
                                polygon.ilevel = int(params[0])
                                polygon.nvertices = int(params[1])
                                polygon.mtype = int(params[2])
                                polygon.filltype = params[3]
                                polygon.debugid = int(params[4])
                                polygon.xmin = int(params[5])
                                polygon.ymin = int(params[6])
                                polygon.xmax = int(params[7])
                                polygon.ymax = int(params[8])
                                polygon.conmax = int(params[9])
                                polygon.res1 = int(params[10])
                                polygon.res2 = int(params[11])
                                polygon.edgemesh = params[12]
                                line = fd.readline()
                                if line.split()[0] == "TOLEVEL":
                                    params = line.split()
                                    polygon.to_level = int(params[1])
                                    polygon.meshingfill = params[2]
                                    polygon.pads = params[3]
                                    line = fd.readline()
                                tlaynam = line.split()
                                gds_indices = tlaynam[1].replace("Stream","").split(":")
                                polygon.gds_stream = int(gds_indices[0])
                                polygon.gds_object = int(gds_indices[1])
                                polygon.inherit = tlaynam[2]
                                line = fd.readline()
                                while line != "END\n":
                                    xvertex = float(line.split()[0])
                                    yvertex = float(line.split()[1])
                                    polygon.vertices.append([xvertex, yvertex])
                                    line = fd.readline()
                                for dlayer in dlayers:
                                    for tlayer in dlayer.tlayers:
                                        if tlayer.gds_stream == polygon.gds_stream and \
                                           tlayer.gds_object == polygon.gds_object:
                                            tlayer.polygons.append(polygon)
                                # Assign port to layer if the current polygon's
                                # debugid matches that of a port's ipolygon
                                for port in ports:
                                    if polygon.debugid == port.ipolygon:
                                        dlayers[polygon.ilevel].ports.append(port)

                            else:
                                line = fd.readline()

                elif line == "CONTROL\n":
                    # Initialize CONTROL block
                    control = Control()
                    project.control = control
                    line = fd.readline()
                    while line != "END CONTROL\n":
                        if line.split()[0] in ["SIMPLE", "STD", "ABS", "OPTIMIZE", "VARSWP", "EXTFILE"]:
                            control.sweep = line.split()[0]
                            line = fd.readline()

                        elif line.split()[0] == "OPTIONS":
                            control.options = line.split()[1]
                            line = fd.readline()

                        elif line.split()[0] == "SUBSPLAM":
                            control.subsplam = line.split()[1] # "Y" or "N"
                            if line.split()[1] == "Y":
                                control.subsplam_subslambda = int(line.split()[2])
                            line = fd.readline()

                        elif line.split()[0] == "EDGECHECK":
                            control.edgecheck = line.split()[1] # "Y" or "N"
                            if line.split()[1] == "Y":
                                control.edgecheck_numlevels = int(line.split()[2])
                            if line.split()[-1] == "TECHLAY":
                                control.edgecheck_checktype = line.split()[-1]
                            line = fd.readline()

                        elif line.split()[0] == "CFMAX":
                            control.cfmax = line.split()[1] # "Y" or "N"
                            if line.split()[1] == "Y":
                                control.cfmax_subfreq = float(line.split()[2])
                            line = fd.readline()

                        elif line.split()[0] == "CEPSY":
                            control.cepsy = line.split()[1] # "Y" or "N"
                            if line.split()[1] == "Y":
                                control.cepsy_epsilon = float(line.split()[2])
                            line = fd.readline()

                        elif line.split()[0] == "FILENAME":
                            control.filename = line.split()[1]
                            line = fd.readline()

                        elif line.split()[0] == "SPEED":
                            control.speed = int(line.split()[1])
                            line = fd.readline()

                        elif line.split()[0] == "RES_ABS":
                            control.res_abs = line.split()[1] # "Y" or "N"
                            if line.split()[1] == "Y":
                                control.res_abs_resolution = float(line.split()[2])
                            line = fd.readline()

                        elif line.split()[0] == "CACHE_ABS":
                            control.cache_abs = int(line.split()[1])
                            line = fd.readline()

                        elif line.split()[0] == "TARG_ABS":
                            control.targ_abs = int(line.split()[1])
                            line = fd.readline()

                        elif line.split()[0] == "Q_ACC":
                            control.q_acc = line.split()[1] # "Y" or "N"
                            line = fd.readline()

                        elif line.split()[0] == "DET_ABS_RES":
                            control.det_abs_res = line.split()[1] # "Y" or "N"
                            line = fd.readline()

                        else:
                            line = fd.readline()

                elif line == "FREQ\n":
                    # Initialize FREQ block
                    freq = Freq()
                    project.freq = freq
                    line = fd.readline()
                    while line != "END FREQ\n":

                        if line.split()[0] == "SIMPLE":
                            freq.sweep = line.split()[0]
                            freq.f1 = float(line.split()[1])
                            freq.f2 = float(line.split()[2])
                            freq.fstep = float(line.split()[3])
                            line = fd.readline()

                        elif line.split()[0] == "ABS":
                            freq.sweep = line.split()[0]
                            freq.f1 = float(line.split()[1])
                            freq.f2 = float(line.split()[2])
                            line = fd.readline()

                        else:
                            line = fd.readline()

                elif line == "OPT\n":
                    # Initialize OPT block
                    opt = Opt()
                    project.opt = opt
                    line = fd.readline()

                    while line != "END OPT\n":
                        # Save all lines
                        opt.lines.append(line)
                        line = fd.readline()

                elif line == "VARSWP\n":
                    # Initialize VARSWP block
                    varswp = Varswp()
                    psweeps = []
                    varswp.psweeps = psweeps
                    project.varswp = varswp
                    line = fd.readline()

                    while line != "END VARSWP\n":

                        if line.split()[0] == "SWEEP":
                            # Initialize parameter sweep
                            psweep = Psweep()
                            psweep.sweeptype = line.split()[0]
                            psweep.f1 = float(line.split()[1])
                            psweep.f2 = float(line.split()[2])
                            psweep.fstep = float(line.split()[3])

                            line = fd.readline()
                            while line.split()[0] == "VAR":
                                var = Var()
                                var.parameter = line.split()[1]
                                var.ytype = line.split()[2]
                                var.min = float(line.split()[3])
                                var.max = float(line.split()[4])
                                var.step = float(line.split()[5])
                                psweep.vars.append(var)
                                line = fd.readline()
                            psweeps.append(psweep)

                        elif line.split()[0] == "ABS_ENTRY":
                            # Initialize parameter sweep
                            psweep = Psweep()
                            psweep.sweeptype = line.split()[0]
                            psweep.f1 = float(line.split()[1])
                            psweep.f2 = float(line.split()[2])

                            line = fd.readline()
                            while line.split()[0] == "VAR":
                                var = Var()
                                var.parameter = line.split()[1]
                                var.ytype = line.split()[2]
                                var.min = float(line.split()[3])
                                var.max = float(line.split()[4])
                                var.step = float(line.split()[5])
                                psweep.vars.append(var)
                                line = fd.readline()
                            psweeps.append(psweep)

                        else:
                            line = fd.readline()

                elif line == "FILEOUT\n":
                    # Initialize FILEOUT block
                    fileout = Fileout()
                    project.fileout = fileout
                    line = fd.readline()

                    while line != "END FILEOUT\n":

                        if line.split()[0] in ["TS", "TOUCH2", "DATA_BANK", "SC", "CSV", "CADENCE", "MDIF", "EBMDIF"]:
                            params = line.split()
                            fileout.filetype = params[0]
                            fileout.embed = params[1]
                            fileout.abs_inc = params[2]
                            fileout.filename = params[3]
                            fileout.comments = params[4]
                            fileout.sig = int(params[5])
                            fileout.partype = params[6]
                            fileout.parform = params[7]
                            fileout.ports = " ".join(params[8:])
                            line = fd.readline()

                        elif line.split()[0] == "FOLDER":
                            fileout.folder = line.split()[1]
                            line = fd.readline()

                        else:
                            line = fd.readline()

                elif line == "SUBDIV\n":
                    # Initialize SUBDIV block
                    subdiv = Subdiv()
                    project.subdiv = subdiv
                    line = fd.readline()

                    while line != "END SUBDIV\n":
                        # Save all lines
                        subdiv.lines.append(line)
                        line = fd.readline()

                elif line == "QSG\n":
                    # Initialize QSG block
                    qsg = Qsg()
                    project.qsg = qsg
                    line = fd.readline()

                    while line not in ["END QSG", "END QSG\n"]:
                        # Save all lines
                        qsg.lines.append(line)
                        line = fd.readline()

                elif line.split()[0] == "END":
                    # Reached the end of a block
                    line = fd.readline()

                else:
                    print("Warning: Ignoring unknown line: {:s}".format(line))
                    line = fd.readline()

    def printLayers(self):
        """
        Prints the layer configuration of the project to the command prompt. For each dielectric layer the following is printed::

            Dielectric layer:  dlayer_index (name)
            Technology layer:  tlayer_index (tlayer_type)
            Port:              portnum (port_type)
            Component:         name (component_type)
        """

        print("\n================== TOP ==================\n")
        for dlayer in self.project.geo.dlayers:
            print("  Dielectric layer:  {ilevel} ({name})".format(**vars(dlayer)))
            for tlayer in dlayer.tlayers:
                print("  Technology layer:  {gds_stream} ({lay_type})".format(**vars(tlayer)))
            for port in dlayer.ports:
                print("  Port:              {portnum} ({type})".format(**vars(port)))
            for component in dlayer.components:
                print("  Component:         {label} of value {compval} ({idealtype})".format(**vars(component)))
            if dlayer.ilevel < len(self.project.geo.dlayers) - 1:
                print("\n================= LVL {ilevel} =================\n".format(**vars(dlayer)))
        print("\n================== GND ==================\n")

    def printParameters(self):
        """
        Prints the defined variable parameters and sweeps set in the project to the command prompt. The frequency/parameter sweeps printed out will run in the Sonnet simulation, and data will be written to the set data file. Variables are printed in following form::

            varname (unittype)
        """

        print("\nVariables:")
        if len(self.project.geo.valvars) == 0:
            print("  No variables defined")
        else:
            for valvar in self.project.geo.valvars:
                print("  {varname} ({unittype})".format(**vars(valvar)))

        if self.project.control.sweep == "VARSWP":
            sweepNumber = 0
            for psweep in self.project.varswp.psweeps:
                sweepNumber += 1
                if psweep.sweeptype == "ABS_ENTRY":
                    print("\nSweep {:n}: Adaptive frequency sweep from {f1:n} to {f2:n} with variables:".format(sweepNumber, **vars(psweep)))
                elif psweep.sweeptype == "SWEEP":
                    print("\nSweep {:n}: Linear frequency sweep from {f1:n} to {f2:n} in steps of {fstep:n} with variables:".format(sweepNumber, **vars(psweep)))
                else:
                    print("\nWarning: Unknown parameter sweep set!")
                for var in psweep.vars:
                    if var.ytype != "N":
                        print("  {parameter} from {min:n} to {max:n} in steps of {step:n}".format(**vars(var)))
        elif self.project.control.sweep == "ABS":
            print("\nAdaptive frequency sweep from {f1:n} to {f2:n}".format(**vars(self.project.freq)))
        elif self.project.control.sweep == "SIMPLE":
            print("\nLinear frequency sweep from {f1:n} to {f2:n} in steps of {fstep:n}".format(**vars(self.project.freq)))
        else:
            print("\nWarning: No sweep set or unknown sweep set!")
        print("\n")

    def printProject(self):
        """
        Prints (overwrites) the Sonnet project with the changes made in SonPy to the Sonnet project file. This function runs before the Sonnet simulation to ensure any changes made in SonPy are recorded in the Sonnet project file Sonnet's simulation software reads.
        """

        with open(self.sonnet_file_path + self.sonnet_file, 'w') as fd:

            # Write every line before the HEADER block
            for line in self.project.preheader.lines:
                fd.write(line)

            # Write HEADER block
            header = self.project.header
            if header == None:
                raise self.exception("HEADER block not initialized.")
            fd.write("HEADER\n")
            for line in header.lines:
                fd.write(line)
            fd.write("END HEADER\n")

            # Write DIM block
            dim = self.project.dim
            if dim == None:
                raise self.exception("DIM block not initialized.")
            fd.write("DIM\n")
            for line in dim.lines:
                fd.write(line)
            fd.write("END DIM\n")

            # Write GEO block
            geo = self.project.geo
            if geo == None:
                raise self.exception("GEO block not initialized.")
            fd.write("GEO\n")

            tmet = geo.tmet
            if tmet != None:
                fd.write("TMET {name} {patternid} {type} ".format(**vars(tmet)))
                for value in tmet.values:
                    fd.write("{:n} ".format(value))
                fd.write("\n")

            bmet = geo.bmet
            if bmet != None:
                fd.write("BMET {name} {patternid} {type} ".format(**vars(bmet)))
                for value in bmet.values:
                    fd.write("{:n} ".format(value))
                fd.write("\n")

            met = geo.met
            if met != None:
                fd.write("MET {name} {patternid} {type} ".format(**vars(met)))
                for value in met.values:
                    fd.write("{:n} ".format(value))
                fd.write("\n")

            bri = geo.bricks
            if bri:
                for bricks in bri:
                    if bricks.isIsotropic:
                        fd.write("BRI ")
                    else:
                        fd.write("BRA ")
                    fd.write("\"{name}\" {patternid} ".format(**vars(bricks)))
                    for value in bricks.values:
                        fd.write("{:n} ".format(value))
                    fd.write("\n")

            box = geo.box
            if box != None:
                fd.write("BOX {nlev} {xwidth:n} {ywidth:n} {xcells2:n} {ycells2:n} {nsubs} {eeff:n}\n".format(**vars(box)))
            else:
                raise self.exception("BOX not initialized.")

            for dlayer in geo.dlayers:
                fd.write("      {thickness:n} {erel:n} {mrel:n} {eloss:n} {mloss:n} {esignma:n} {nzpart} \"{name}\"\n".format(**vars(dlayer)))

            for dlayer in geo.dlayers:
                for tlayer in dlayer.tlayers:
                    fd.write("TECHLAY {lay_type} {lay_name} {dxf_layer} {gds_stream} {gds_object}\n".format(**vars(tlayer)))
                    if tlayer.type != "MET POL":
                        fd.write("{type}\n".format(**vars(tlayer)))
                    fd.write("{ilevel} {nvertices} {mtype} {filltype} {debugid} {xmin:n} {ymin:n} {xmax:n} {ymax:n} {conmax:n} {res1:n} {res2:n} {edgemesh}\n".format(**vars(tlayer)))
                    if tlayer.lay_type == "VIA":
                        fd.write("TOLEVEL {to_level} {meshingfill} {pads}\n".format(**vars(tlayer)))
                    fd.write("END\nEND\n")

            valvars = geo.valvars
            for valvar in valvars:
                fd.write("VALVAR {varname} {unittype} {value:n} \"{description}\"\n".format(**vars(valvar)))

            lorgn = geo.lorgn
            if lorgn != None:
                fd.write("LORGN {x:n} {y:n} {locked}\n".format(**vars(lorgn)))

            for dlayer in geo.dlayers:
                for port in dlayer.ports:
                    fd.write("POR1 {type}\n".format(**vars(port)))
                    fd.write("POLY {ipolygon} 1\n".format(**vars(port)))
                    fd.write("{ivertex}\n".format(**vars(port)))
                    fd.write("{portnum} {resist:n} {react:n} {induct:n} {capac:n} {xcoord:n} {ycoord:n}\n".format(**vars(port)))

            for dlayer in geo.dlayers:
                for component in dlayer.components:
                    fd.write("SMD {levelnum} \"{label}\"\n".format(**vars(component)))
                    fd.write("ID {objectid}\n".format(**vars(component)))
                    fd.write("GNDREF {gndref}\n".format(**vars(component)))
                    fd.write("TWTYPE {twtype}\n".format(**vars(component)))
                    fd.write("SBOX {leftpos:n} {rightpos:n} {toppos:n} {bottompos:n}\n".format(**vars(component)))
                    fd.write("PBSHW {pbshw}\n".format(**vars(component)))
                    fd.write("LPOS {xpos:n} {ypos:n}\n".format(**vars(component)))
                    fd.write("TYPE IDEAL {idealtype} ".format(**vars(component)))
                    # Write compval either as a variable parameter or float
                    if type(component.compval) == str:
                        fd.write("\"{compval}\"\n".format(**vars(component)))
                    else:
                        fd.write("{compval:n}\n".format(**vars(component)))
                    fd.write("SMDP {smdp1_levelnum} {smdp1_x:n} {smdp1_y:n} {smdp1_orientation} {smdp1_portnum} {smdp1_pinnum}\n".format(**vars(component)))
                    fd.write("SMDP {smdp2_levelnum} {smdp2_x:n} {smdp2_y:n} {smdp2_orientation} {smdp2_portnum} {smdp2_pinnum}\n".format(**vars(component)))
                    fd.write("END\n")

            fd.write("NUM {npoly}\n".format(**vars(geo)))

            for dlayer in geo.dlayers:
                for tlayer in dlayer.tlayers:
                    for polygon in tlayer.polygons:
                        # Make sure the ilevel and to_level reflects that of tlayer
                        polygon.ilevel = tlayer.ilevel
                        polygon.to_level = tlayer.to_level
                        fd.write("{type}\n".format(**vars(polygon)))
                        fd.write("{ilevel} {nvertices} {mtype} {filltype} {debugid} {xmin:n} {ymin:n} {xmax:n} {ymax:n} {conmax:n} {res1:n} {res2:n} {edgemesh}\n".format(**vars(polygon)))
                        if tlayer.lay_type == "VIA":
                            fd.write("TOLEVEL {to_level} {meshingfill} {pads}\n".format(**vars(polygon)))
                        fd.write("TLAYNAM Stream{gds_stream}:{gds_object} {inherit}\n".format(**vars(polygon)))
                        for vertex in polygon.vertices:
                            fd.write("{:n} {:n}\n".format(vertex[0], vertex[1]))
                        fd.write("END\n")

            fd.write("END GEO\n")

            # Write CONTROL block
            control = self.project.control
            if control != None:
                fd.write("CONTROL\n")

                if control.sweep != None:
                    fd.write("{sweep}\n".format(**vars(control)))

                if control.options != None:
                    fd.write("OPTIONS {options}\n".format(**vars(control)))

                if control.subsplam != None:
                    fd.write("SUBSPLAM {subsplam}".format(**vars(control)))
                    if control.subsplam_subslambda != None:
                        fd.write(" {subsplam_subslambda}".format(**vars(control)))
                    fd.write("\n")

                if control.edgecheck != None:
                    fd.write("EDGECHECK {edgecheck}".format(**vars(control)))
                    if control.edgecheck_numlevels != None:
                        fd.write(" {edgecheck_numlevels}".format(**vars(control)))
                    if control.edgecheck_checktype != None:
                        fd.write(" {edgecheck_checktype}".format(**vars(control)))
                    fd.write("\n")

                if control.cfmax != None:
                    fd.write("CFMAX {cfmax}".format(**vars(control)))
                    if control.cfmax_subfreq != None:
                        fd.write(" {cfmax_subfreq:n}".format(**vars(control)))
                    fd.write("\n")

                if control.cepsy != None:
                    fd.write("CEPSY {cepsy}".format(**vars(control)))
                    if control.cepsy != None:
                        fd.write(" {cepsy_epsilon:n}".format(**vars(control)))
                    fd.write("\n")

                if control.filename != None:
                    fd.write("FILENAME {filename}\n".format(**vars(control)))

                if control.speed != None:
                    fd.write("SPEED {speed}\n".format(**vars(control)))

                if control.res_abs != None:
                    fd.write("RES_ABS {res_abs}".format(**vars(control)))
                    if control.res_abs_resolution != None:
                        fd.write(" {res_abs_resolution:n}".format(**vars(control)))
                    fd.write("\n")

                if control.cache_abs != None:
                    fd.write("CACHE_ABS {cache_abs}\n".format(**vars(control)))

                if control.targ_abs != None:
                    fd.write("TARG_ABS {targ_abs}\n".format(**vars(control)))

                if control.q_acc != None:
                    fd.write("Q_ACC {q_acc}\n".format(**vars(control)))

                if control.det_abs_res != None:
                    fd.write("DET_ABS_RES {det_abs_res}\n".format(**vars(control)))

                fd.write("END CONTROL\n")

            # Write FREQ block
            freq = self.project.freq
            if freq != None:
                fd.write("FREQ\n")

                if freq.sweep == "SIMPLE":
                    fd.write("{sweep} {f1:n} {f2:n} {fstep:n}\n".format(**vars(freq)))

                elif freq.sweep == "ABS":
                    fd.write("{sweep} {f1:n} {f2:n}\n".format(**vars(freq)))

                fd.write("END FREQ\n")

            # Write OPT block
            opt = self.project.opt
            if opt != None:
                fd.write("OPT\n")
                for line in opt.lines:
                    fd.write(line)
                fd.write("END OPT\n")

            # Write VARSWP block
            varswp = self.project.varswp
            if varswp != None:
                fd.write("VARSWP\n")

                for psweep in varswp.psweeps:
                    fd.write("{sweeptype} {f1:n} {f2:n}".format(**vars(psweep)))
                    if psweep.sweeptype == "SWEEP":
                        fd.write(" {fstep:n}".format(**vars(psweep)))
                    fd.write("\n")
                    for var in psweep.vars:
                        fd.write("VAR {parameter} {ytype} {min:n} {max:n} {step:n}\n".format(**vars(var)))
                fd.write("END\n")

                fd.write("END VARSWP\n")

            # Write FILEOUT block
            fileout = self.project.fileout
            if fileout != None:
                fd.write("FILEOUT\n")

                fd.write("{filetype} {embed} {abs_inc} {filename} {comments} {sig} {partype} {parform} {ports}\n".format(**vars(fileout)))
                if fileout.folder != None:
                   fd.write("FOLDER {folder}\n".format(**vars(fileout)))

                fd.write("END FILEOUT\n")

            # Write SUBDIV block
            subdiv = self.project.subdiv
            if subdiv != None:
                fd.write("SUBDIV\n")
                for line in subdiv.lines:
                    fd.write(line)
                fd.write("END SUBDIV\n")

            # Write QSG block
            qsg = self.project.qsg
            if qsg != None:
                fd.write("QSG\n")
                for line in qsg.lines:
                    fd.write(line)
                fd.write("END QSG")

    ########################################################################
    # PROJECT GEOMETRY (LAYERS, PORTS, COMPONENTS ECT.)                    #
    ########################################################################

    def getBoundingBox(self):
        """
        Gets the bounding box for the polygons in the project.

        """
        xvertices, yvertices = [], []
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                for polygon in tlayer.polygons:
                    # check if polygon is a sonnet glitch where all the points are the same
                    glitched_polygon = all(x==polygon.vertices[0] for x in polygon.vertices)
                    if not glitched_polygon:
                        for vertex in polygon.vertices:
                            xvertices.append(vertex[0])
                            yvertices.append(vertex[1])

        xmin, ymin = min(xvertices), min(yvertices)
        xmax, ymax = max(xvertices), max(yvertices)

        return[[xmin,ymin],[xmax,ymax]]


    def cropBox(self, xcellsize=1, ycellsize=1):
        """
        Crops the bounding box (used in Sonnet to confine the simulation space) to the circuit of the circuit.

        :param xcellsize: Cellsize in x direction.
        :param ycellsize: Cellsize in y direction.
        :type xcellsize: float
        :type ycellsize: float

        """

        # Technical description for delevopers:
        # Crops the BOX to the circuit and set the cellsize in x and y direction, and
        # sets the local origin (LORGN in GEO block) in order to place point correctly
        # If the circuit is rectangular, this ensures that ports added to the
        # edges of the circuit is also at the edge of the BOX

        xvertices, yvertices = [], []
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                for polygon in tlayer.polygons:
                    # check if the polygon is a sonnet or gds glitch where all the points are the same
                    glitched_polygon = all(x == polygon.vertices[0] for x in polygon.vertices)
                    if not glitched_polygon:
                        for vertex in polygon.vertices:
                            xvertices.append(vertex[0])
                            yvertices.append(vertex[1])

        xmin, ymin = min(xvertices), min(yvertices)
        xmax, ymax = max(xvertices), max(yvertices)
        # Define or redefine the local origin (LORGN)
        lorgn = Lorgn()
        lorgn.x = 0
        lorgn.y = ymax - ymin
        self.project.geo.lorgn = lorgn
        # Redefine the confining box (BOX)
        self.project.geo.box.xcells2 = int(2*round((xmax - xmin)/xcellsize))
        self.project.geo.box.ycells2 = int(2*round((ymax - ymin)/ycellsize))

        self.project.geo.box.xwidth = int(round((xmax - xmin)/xcellsize))*xcellsize
        self.project.geo.box.ywidth = int(round((ymax - ymin)/ycellsize))*ycellsize

        # Shift the circuit (all polygons, components and polygons)
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                for polygon in tlayer.polygons:
                    for vertex in polygon.vertices:
                        vertex[0] += -xmin
                        vertex[1] += -ymin
            for port in dlayer.ports:
                port.xcoord += -xmin
                port.ycoord += -ymin
            for component in dlayer.components:
                component.xpos += -xmin
                component.smdp1_x += -xmin
                component.smdp2_x += -xmin
                component.leftpos += -xmin
                component.rightpos += -xmin
                component.ypos += -ymin
                component.smdp1_y += -ymin
                component.smdp2_y += -ymin
                component.toppos += -ymin
                component.bottompos += -ymin

    # def mergePolygons(self):
    #     """
    #     Merges all adjacent polygons. This operations reduces the number of polygons thereby saving simulation time, but it does not changed the physical system or the simulation results.
    #     """
    #
    #     for dlayer in self.project.geo.dlayers:
    #         for tlayer in dlayer.tlayers:
    #             adjacentPolygons = []
    #             polygons = tlayer.polygons
    #             # Loop over pairs of different polygons
    #             for i in range(0, len(polygons)):
    #                 # Primary polygon
    #                 x_pri = [xvertex for [xvertex, yvertex] in polygons[i].vertices]
    #                 y_pri = [yvertex for [xvertex, yvertex] in polygons[i].vertices]
    #                 for j in range(i + 1, len(polygons)):
    #                     # Secondary polygon
    #                     for vertex in range(0, polygons[j].nvertices - 1):
    #                         x = polygon.vertices[vertex][0]
    #                         y = polygon.vertices[vertex][1]
    #                         # Check if point is within primary polygon (quick test)
    #                         if x >= min(x_pri) and x <= max(x_pri) and \
    #                            y >= min(y_pri) and y <= max(y_pri):
    #                             # Check if point lies along primary polygon edge (slow test)
    #                             for
    #
    #
    #                         x0 = polygon.vertices[vertex][0]
    #                         y0 = polygon.vertices[vertex][1]
    #                         x1 = polygon.vertices[vertex + 1][0]
    #                         y1 = polygon.vertices[vertex + 1][1]
    #
    #                 # Primary polygon
    #                 x_pri = [xvertex for [xvertex, yvertex] in polygons[i].vertices]
    #                 y_pri = [yvertex for [xvertex, yvertex] in polygons[i].vertices]
    #                 for j in range(i + 1, len(polygons)):
    #                     # Secondary polygon
    #                     x_sec = [xvertex for [xvertex, yvertex] in polygons[j].vertices]
    #                     y_sec = [yvertex for [xvertex, yvertex] in polygons[j].vertices]
    #                     # If they cannot be adjacent then skip this pair...
    #                     if min(x_sec) > max(x_pri) or max(x_sec) < min(x_pri) or \
    #                        min(y_sec) > max(y_pri) or max(y_sec) < min(y_pri):
    #                         break
    #                     # ...else we see if vertex points of the primary polygon
    #                     # lie on any of the primary polygon edges
    #                     else:
    #                         for k in range()
    #
    #                     # MAIN PROBLEM: How to make sure that all connected polygons get merged?
    #
    #
    #
    #                     for
    #                     # Check if point is within primary polygon (quick test)
    #                     if x >= xmin and x <= xmax and \
    #                        y >= ymin and y <= ymax:
    #                         # Check if point lies along primary polygon edge (slow test)
    #
    #
    #
    #
    #                 # Update nvertices of the polygon
    #
    #                 # Update npoly in the GEO block


    def mapPoint(self, xcoord, ycoord):
        # Internal use only.

        # Sonnet computes points relative to the circuit's upper left corner (ULC),
        # but it's easier for the user to specify points relative to the lower
        # left corner (LLC). This function takes an input point (xcoord, ycoord)
        # from the user's LLC system and returns the point in Sonnet's ULC system

        yvertices = []
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                for polygon in tlayer.polygons:
                    for vertex in polygon.vertices:
                        yvertices.append(vertex[1])

        return xcoord, (max(yvertices) - min(yvertices)) - ycoord

    def addPort(self, xcoord, ycoord, xmargin=0.005, ymargin=0.005, **kwargs):
        """
        Adds a port (of standard type). Since Sonnet's GDSII translator ever so slightly shifts the coordinates used in the GDSII file it is often necessary to look for attachment points with a small margin. For instance, say you originally planned to add a port at the edge of your circuit at (0, 100). After the GDSII file has been translated into a Sonnet project file, this points has shifted to, say, (0, 99.997). Trying to add the port at (0, 100) will throw an error because this point is no longer at the edge of the circuit (or any of the polygons). Looking for possible attachment points (i.e. polygon edges) with a small margin will find to correct point (0, 99.997).

        :param float xcoord: Attachment x coordinate.
        :param float ycoord: Attachment y coordinate.
        :param float xmargin: Margin in x direction.
        :param float ymargin: Margin in y direction.

        Keyword arguments:

        :param float resist: Port parameter defined in [Son15]_ under POR1.
        :param float react: Port parameter defined in [Son15]_ under POR1.
        :param float induct: Port parameter defined in [Son15]_ under POR1.
        :param float capac: Port parameter defined in [Son15]_ under POR1.
        :param tlayer_index: Restrict the search for attachment points to a single or list of technology layers (useful if several technology layers have overlapping polygon edges at the attachment point).
        :type tlayer_index: int or list of ints
        """

        # Technical description for delevopers:
        # Add a POR1 STD definition in the GEO block
        # The DIAGALLOWED line is not supported
        # The default port number is the number of existing ports (including
        # the two ports in each ideal component) + 1.
        # The function looks for attachement points within xcoord ± xmargin
        # in the x direction and ycoord ± ymargin in the y direction. The
        # attachment point closest to (xcoord, ycoord) is picked.
        # For several equally good attachment points the first one is picked.
        # By default we look for attachment points among all technology
        # layers, but the search range can be decreased by setting the keyword
        # argument "tlayer_index" to a single integer or list of integers
        # with the gds indices of the technology layers.

        port = Port()
        xcoord, ycoord = self.mapPoint(xcoord, ycoord)

        # List all technology layers (default search range)
        allTlayers = []
        numberOfPorts = 0
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                allTlayers.append(tlayer)
            for oldport in dlayer.ports:
                numberOfPorts += 1
            for component in dlayer.components:
                numberOfPorts += 2
        searchTlayers = allTlayers
        port.portnum = numberOfPorts + 1

        # Get keyword arguments from user input
        for key, value in kwargs.items():
            if key == "resist":
                port.resist = value
            elif key == "react":
                port.react = value
            elif key == "induct":
                port.induct = value
            elif key == "capac":
                port.capac = value
            elif key == "tlayer_index":
                # Redefine the tlayer search range
                if type(value) == int:
                    value = [value]
                searchTlayers = []
                for tlayer in allTlayers:
                    if tlayer.gds_stream in value:
                        searchTlayers.append(tlayer)
            else:
                raise self.exception("Invalid keyword argument.")

        # Look for possible attachment points within the search tlayers
        # (Remember that we are a now in Sonnets coordinate system where
        # all points are relative the the circuit's upper left corner)
        candidateAttachments = []
        for tlayer in searchTlayers:
            for polygon in tlayer.polygons:
                for vertex in range(0, polygon.nvertices - 1):
                    x0 = polygon.vertices[vertex][0]
                    y0 = polygon.vertices[vertex][1]
                    x1 = polygon.vertices[vertex + 1][0]
                    y1 = polygon.vertices[vertex + 1][1]
                    # If the attachment point is close enough to the polygon edge,
                    # we save the vertex index (ivertex), polygon index (ipolygon),
                    # a (simplified) distance error and the tlayer index
                    if min(x0,x1) - xmargin <= xcoord and \
                       xcoord <= max(x0,x1) + xmargin and \
                       min(y0,y1) - ymargin <= ycoord and \
                       ycoord <= max(y0,y1) + ymargin:
                        if x0 == x1:
                            error = (xcoord - x0)**2
                            # The nearest edge point
                            xnew = x0
                            if ycoord > max(y0,y1):
                                ynew = max(y0,y1)
                            elif ycoord < min(y0,y1):
                                ynew = min(y0,y1)
                            else:
                                ynew = ycoord
                            candidateAttachments.append([polygon.debugid, vertex, error, tlayer.ilevel, xnew, ynew])
                        elif y0 == y1:
                            error = (ycoord - y0)**2
                            # The nearest edge point
                            ynew = y0
                            if xcoord > max(x0,x1):
                                xnew = max(x0,x1)
                            elif xcoord < min(x0,x1):
                                xnew = min(x0,x1)
                            else:
                                xnew = xcoord
                            candidateAttachments.append([polygon.debugid, vertex, error, tlayer.ilevel, xnew, ynew])
                        else:
                            error = ycoord - y0 - (y1 - y0)/(x1 - x0)*(xcoord - x0)**2 \
                                  + xcoord - x0 - (x1 - x0)/(y1 - y0)*(ycoord - y0)**2
                            # The nearest edge point
                            t = ( (x0-x1)*(x0-xcoord) + (y0-y1)*(y0-ycoord) ) / ( (x1-x0)**2 + (y1-y0)**2 )
                            xnew = x0 + (x1-x0)*t
                            ynew = y0 + (y1-y0)*t
                            candidateAttachments.append([polygon.debugid, vertex, error, tlayer.ilevel, xnew, ynew])

        # Evalute the found potential polygon edges to attach to
        if len(candidateAttachments) == 0:
            raise self.exception("No polygon edges found to attach port to!")
        # Sort according to error and add the best attachment point to the port
        candidateAttachments.sort(key=lambda item: abs(item[2]))
        [ipolygon, ivertex, error, ilevel, xnew, ynew] = candidateAttachments[0]
        port.ipolygon = ipolygon
        port.ivertex = ivertex
        port.xcoord = xnew
        port.ycoord = ynew

        # Add the port to the dlayer
        self.project.geo.dlayers[ilevel].ports.append(port)

    def addComponent(self, x1, y1, x2, y2, tlayer_index, component_type="ind", value=10, xmargin=0.005, ymargin=0.005, **kwargs):
        """
        Adds an ideal component. Attachment point margins are the same as for :func:`addPort`.

        :param float x1: Attachment x coordinate for the first port.
        :param float y1: Attachment y coordinate for the first port.
        :param float x2: Attachment x coordinate for the second port.
        :param float y2: Attachment y coordinate for the second port.
        :param float xmargin: Margin in x direction.
        :param float ymargin: Margin in y direction.
        :param int tlayer_index: Index (gds stream number) of the technology layer the component will live in.
        :param str component_type: Type of component. Should be ``"ind"`` (inductor), ``"cap"`` (capacitor) or ``"res"`` (resistor).
        :param float value: Value of the component in units suitable for the component type.

        Keyword arguments:

        :param str name: Name for the component. Default is ``L``, ``C``, ``R`` followed by a number for inductors, capacitors and resistors. For instance, the first ideal capacitor is named ``"L1"``, the next ``"L2"`` ect.
        :param int smdp1_portnum: Port number for first port, see [Son15]_ under SMD. Default is the number of existing ports + 1.
        :param int smdp1_pinnum: See [Son15]_ under SMD.
        :param int smdp2_portnum: Port number for second port, see [Son15]_ under SMD. Default is the number of existing ports + 2.
        :param int smdp2_pinnum: See [Son15]_ under SMD.
        """

        # Technical description for delevopers:
        # Adds a SMD definition of TYPE IDEAL in the GEO block (after LORGN)
        # The component type is "ind" for inductor, "cap" for capacitor, or
        # "res" for resistor.
        # The value argument sets the inductance/capacitance/resistance
        # The tlayer argument is the gds index of the technology layer
        # The component's endpoints are (x1,y1) and (x2,y2) in LLC system
        # Only a simple ideal components are supported, thus the following
        # do not appear in the statement of the component: TWTYPE FEED or
        # CUST, TWVALUE, DRP1, PBSHW Y, PBOX, PKG or any TYPE other than IDEAL
        # Like in the addPort function we attach to nearby polygon edges.

        component = Component()
        component.compval = value
        xcoord1, ycoord1 = self.mapPoint(x1, y1)
        xcoord2, ycoord2 = self.mapPoint(x2, y2)

        # Fill out some default parameter values
        if component_type == "ind":
            component.idealtype = "IND"
            nametag = "L"
        elif component_type == "cap":
            component.idealtype = "CAP"
            nametag = "C"
        elif component_type == "res":
            component.idealtype = "RES"
            nametag = "R"
        else:
            raise self.exception("Invalid component type.")

        numberOfPorts = 0
        numberOfComponents = 0
        numberOfSameComponents = 0
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                if tlayer.gds_stream == tlayer_index:
                    component.levelnum = dlayer.ilevel
                    component.smdp1_levelnum = dlayer.ilevel
                    component.smdp2_levelnum = dlayer.ilevel
            for oldComponent in dlayer.components:
                numberOfPorts += 2
                numberOfComponents += 1
                if oldComponent.idealtype == component.idealtype:
                    numberOfSameComponents += 1
            for port in dlayer.ports:
                numberOfPorts += 1

        # Default labelling is "L1", "L2" ect. for inductors and similarly
        # "C1", "R1" ect. for capacitors and resistors
        component.label = "\"" + nametag + str(numberOfSameComponents + 1) + "\""
        component.objectid = numberOfComponents + 1
        component.smdp1_portnum = numberOfPorts + 1
        component.smdp2_portnum = numberOfPorts + 2
        component.smdp1_pinnum = 1
        component.smdp2_pinnum = 2

        # Sanity check of input tlayer to attach to
        if component.levelnum == None:
            raise self.exception("No technology layer to attach to!")

        # Look for possible attachment points on nearby polygon edges
        # (Remember that we are a now in Sonnets coordinate system where
        # all points are relative the the circuit's upper left corner)
        candidateAttachments1 = []
        candidateAttachments2 = []
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                for polygon in tlayer.polygons:
                    for vertex in range(0, polygon.nvertices - 1):
                        x0 = polygon.vertices[vertex][0]
                        y0 =  polygon.vertices[vertex][1]
                        x1 = polygon.vertices[vertex + 1][0]
                        y1 = polygon.vertices[vertex + 1][1]
                        # If the attachment point of port number 1 is close
                        # enough to the polygon edge we save it
                        if min(x0,x1) - xmargin <= xcoord1 and \
                           xcoord1 <= max(x0,x1) + xmargin and \
                           min(y0,y1) - ymargin <= ycoord1 and \
                           ycoord1 <= max(y0,y1) + ymargin:
                            if x0 == x1:
                                error = (xcoord1 - x0)**2
                                # The nearest edge point
                                xnew = x0
                                if ycoord1 > max(y0,y1):
                                    ynew = max(y0,y1)
                                elif ycoord1 < min(y0,y1):
                                    ynew = min(y0,y1)
                                else:
                                    ynew = ycoord1
                                candidateAttachments1.append([error, xnew, ynew])
                            elif y0 == y1:
                                error = (ycoord1 - y0)**2
                                # The nearest edge point
                                ynew = y0
                                if xcoord1 > max(x0,x1):
                                    xnew = max(x0,x1)
                                elif xcoord1 < min(x0,x1):
                                    xnew = min(x0,x1)
                                else:
                                    xnew = xcoord1
                                candidateAttachments1.append([error, xnew, ynew])
                            else:
                                error = ycoord1 - y0 - (y1 - y0)/(x1 - x0)*(xcoord1 - x0)**2 \
                                      + xcoord1 - x0 - (x1 - x0)/(y1 - y0)*(ycoord1 - y0)**2
                                # The nearest edge point
                                t = ( (x0-x1)*(x0-xcoord1) + (y0-y1)*(y0-ycoord1) ) / ( (x1-x0)**2 + (y1-y0)**2 )
                                xnew = x0 + (x1-x0)*t
                                ynew = y0 + (y1-y0)*t
                                candidateAttachments1.append([error, xnew, ynew])
                        # And similarly save points for port nmber 2
                        if min(x0,x1) - xmargin <= xcoord2 and \
                           xcoord2 <= max(x0,x1) + xmargin and \
                           min(y0,y1) - ymargin <= ycoord2 and \
                           ycoord2 <= max(y0,y1) + ymargin:
                            if x0 == x1:
                                error = (xcoord2 - x0)**2
                                # The nearest edge point
                                xnew = x0
                                if ycoord2 > max(y0,y1):
                                    ynew = max(y0,y1)
                                elif ycoord2 < min(y0,y1):
                                    ynew = min(y0,y1)
                                else:
                                    ynew = ycoord2
                                candidateAttachments2.append([error, xnew, ynew])
                            elif y0 == y1:
                                error = (ycoord2 - y0)**2
                                # The nearest edge point
                                ynew = y0
                                if xcoord2 > max(x0,x1):
                                    xnew = max(x0,x1)
                                elif xcoord2 < min(x0,x1):
                                    xnew = min(x0,x1)
                                else:
                                    xnew = xcoord2
                                candidateAttachments2.append([error, xnew, ynew])
                            else:
                                error = ycoord2 - y0 - (y1 - y0)/(x1 - x0)*(xcoord2 - x0)**2 \
                                      + xcoord2 - x0 - (x1 - x0)/(y1 - y0)*(ycoord2 - y0)**2
                                # The nearest edge point
                                t = ( (x0-x1)*(x0-xcoord1) + (y0-y1)*(y0-ycoord2) ) / ( (x1-x0)**2 + (y1-y0)**2 )
                                xnew = x0 + (x1-x0)*t
                                ynew = y0 + (y1-y0)*t
                                candidateAttachments2.append([error, xnew, ynew])

        # Evalute the found potential polygon edges to attach to
        if len(candidateAttachments1) == 0:
            raise self.exception("No polygon edges found to attach component port 1 to!")
        if len(candidateAttachments2) == 0:
            raise self.exception("No polygon edges found to attach component port 2 to!")
        # Sort according to error and add the best attachment point to the port
        candidateAttachments1.sort(key=lambda item: item[2])
        candidateAttachments2.sort(key=lambda item: item[2])
        [error1, xnew1, ynew1] = candidateAttachments1[0]
        [error2, xnew2, ynew2] = candidateAttachments2[0]

        # Redefine the port coordinates
        x1, y1 = xnew1, ynew1
        x2, y2 = xnew2, ynew2
        component.smdp1_x = x1
        component.smdp1_y = y1
        component.smdp2_x = x2
        component.smdp2_y = y2

        # Figure out the direction of the component (vertical or horizontal)
        # and define schematic box positions and label position (in the GUI)
        # Note: all positions are relative to upper left corner (ULC)
        sbox_height = abs(x2-x1)/6
        sbox_width = abs(x2-x1)/2

        if y1 == y2 and x1 < x2:
            component.smdp1_orientation = "L"
            component.smdp2_orientation = "R"
            component.leftpos = x1 + sbox_width/2
            component.rightpos = x2 - sbox_width/2
            component.toppos = y1 - sbox_height/2
            component.bottompos = y1 + sbox_height/2
            component.xpos = x1 + abs(x2-x1)/2
            component.ypos = component.toppos

        elif y1 == y2 and x1 > x2:
            component.smdp1_orientation = "R"
            component.smdp2_orientation = "L"
            component.leftpos = x2 + sbox_width/2
            component.rightpos = x1 - sbox_width/2
            component.toppos = y1 - sbox_height/2
            component.bottompos = y1 + sbox_height/2
            component.xpos = x2 + abs(x2-x1)/2
            component.ypos = component.toppos

        elif y1 < y2 and x1 == x2:
            component.smdp1_orientation = "T"
            component.smdp2_orientation = "B"
            component.leftpos = x1 - sbox_height/2
            component.rightpos = x1 + sbox_height/2
            component.toppos = y1 + sbox_width/2
            component.bottompos = y2 - sbox_width/2
            component.xpos = component.leftpos
            component.ypos = y1 + abs(y2-y1)/2

        elif y1 > y2 and x1 == x2:
            component.smdp1_orientation = "B"
            component.smdp2_orientation = "T"
            component.leftpos = x1 - sbox_height/2
            component.rightpos = x1 + sbox_height/2
            component.toppos = y2 + sbox_width/2
            component.bottompos = y1 - sbox_width/2
            component.xpos = component.leftpos
            component.ypos = y2 + abs(y2-y1)/2

        else:
            raise self.exception("Component neither vertical nor horizontal!")

        # Update parameters with keyword arguments from the user
        for key, value in kwargs.items():
            if key in "name":
                port.label = value
            elif key == "smdp1_portnum":
                port.smdp1_portnum = value
            elif key == "smdp1_pinnum":
                port.smdp1_pinnum = value
            elif key == "smdp2_portnum":
                port.smdp2_portnum = value
            elif key == "smdp2_pinnum":
                port.smdp2_pinnum = value
            else:
                raise self.exception("Invalid keyword argument.")

        self.project.geo.dlayers[component.levelnum].components.append(component)

    def removeDlayer(self, dlayer_index=0):
        """
        Removes a dielectric layer including any technology layers, ports or components that reside in the layer. Any via technology layers that extend to this dielectric layer are also removed.

        :param int dlayer_index: Index of the layer that will be removed.
        """

        if dlayer_index > len(self.project.geo.dlayers) - 1:
            raise self.error("Dlayer out of bound. Cannot remove non-existing layer.")

        # Remove any VIA tlayers that extend to the doomed layer
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                if tlayer.lay_type == "VIA" and tlayer.to_level == dlayer_index:
                    dlayer.tlayers.remove(tlayer)

        # Shift all layers below the doomed layer one up
        for dlayer in self.project.geo.dlayers[dlayer_index + 1:]:
            dlayer.ilevel += -1
            for tlayer in dlayer.tlayers:
                tlayer.ilevel += -1
                for polygon in tlayer.polygons:
                    polygon.ilevel += -1
                # Shift VIA layers that extend below the doomed layer
                if tlayer.type == "VIA" and tlayer.to_level > dlayer_index:
                    tlayer.to_level += -1
                    for polygon in tlayer.polygons:
                        polygon.to_level += -1
            for component in dlayer.components:
                component.levelnum += -1
                component.smdp1_levelnum += -1
                component.smdp2_levelnum += -1

        del self.project.geo.dlayers[dlayer_index]
        self.project.geo.box.nlev += -1

    def removeEmptyDlayers(self):
        """
        Removes all dielectric layers that do not contain any technology layers except for the bottom dielectric layer, which should always be empty.
        """

        numberOfNonEmptyLayers = 0
        for dlayer in self.project.geo.dlayers[:-1]:
            if [len(dlayer.tlayers), len(dlayer.ports), len(dlayer.components)] == [0,0,0]:
                self.removeDlayer(numberOfNonEmptyLayers)
            else:
                numberOfNonEmptyLayers += 1

    def collapseDlayers(self):
        """
        Sends all technology layers, ports and components to the top dielectric layer (``dlayer_index = 0``) and removes all dielectric layers except for the two top layers.

        This function is run after the GDSII translator for the following reason. Say the GDSII has a layer with gds stream number 23. This layer will become a technology layer in a dielectric layer of index 23, so a lot of empty dielectric layers are created in this process. This function removes these layers. After this operation there is an empty bottom dielctric layer (as there should be) and a single dielctric layer on top.
        """

        tlayersAll = []
        portsAll = []
        componentsAll = []

        # Save layers and set all layer indices to 0
        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                tlayer.ilevel = 0
                tlayersAll.append(tlayer)
                for polygon in tlayer.polygons:
                    polygon.ilevel = 0
                if tlayer.type == "VIA":
                    tlayer.to_level = 0
                    for polygon in tlayer.polygons:
                        polygon.to_level = 0
            for port in dlayer.ports:
                portsAll.append(port)
            for component in dlayer.components:
                component.levelnum = 0
                component.smdp1_levelnum = 0
                component.smdp2_levelnum = 0
                componentsAll.append(component)

        # Remove all but the two top layers
        while len(self.project.geo.dlayers) > 2:
            del self.project.geo.dlayers[-1]

        # Put everything in dlayer 0
        self.project.geo.dlayers[0].tlayers = tlayersAll
        self.project.geo.dlayers[0].ports = portsAll
        self.project.geo.dlayers[0].components = componentsAll
        self.project.geo.box.nlev = 1

    def addDlayer(self, dlayer_index=0, **kwargs):
        """
        Adds a dielectric layer to the project.

        :param int dlayer_index: Index of the dielctric layer after the addition. By default the new layer is added to the top.

        Keyword arguments:

        :param float thickness: See [Son15]_ under BOX. Default is 0.
        :param float erel: See [Son15]_ under BOX. Default is 1.
        :param float mrel: See [Son15]_ under BOX. Default is 1.
        :param float eloss: See [Son15]_ under BOX. Default is 0.
        :param float mloss: See [Son15]_ under BOX. Default is 0.
        :param float esignma: See [Son15]_ under BOX. Default is 0.
        :param str name: See [Son15]_ under BOX. Default is ``"New layer"``.
        """

        dlayerNew = Dlayer()
        dlayerNew.ilevel = dlayer_index

        # Get keyword arguments from user input
        for key, value in kwargs.items():
            if key == "thickness":
                dlayerNew.thickness = value
            elif key == "erel":
                dlayerNew.erel = value
            elif key == "mrel":
                dlayerNew.mrel = value
            elif key == "eloss":
                dlayerNew.eloss = value
            elif key == "mloss":
                dlayerNew.mloss = value
            elif key == "esignma":
                dlayerNew.esignma = value
            elif key == "name":
                dlayerNew.name = value
            else:
                raise self.exception("Invalid keyword argument.")

        # Shift all layers below the new layer one layer index up
        for dlayer in self.project.geo.dlayers[dlayer_index:]:
            dlayer.ilevel += 1
            for tlayer in dlayer.tlayers:
                tlayer.ilevel += 1
                for polygon in tlayer.polygons:
                    polygon.ilevel += 1
                # Shift VIA layers that extend below the new layer
                if tlayer.type == "VIA" and tlayer.to_level > dlayer_index - 1:
                    tlayer.to_level += 1
                    for polygon in tlayer.polygons:
                        polygon.to_level += 1
            for component in dlayer.components:
                component.levelnum += 1
                component.smdp1_levelnum += 1
                component.smdp2_levelnum += 1

        # Insert the new dlayer
        self.project.geo.dlayers.insert(dlayer_index, dlayerNew)
        self.project.geo.box.nlev += 1

    def setDlayer(self, dlayer_index, **kwargs):
        """
        Sets the parameters of a dielectric layer to those specified by the keyword arguments. Only parameters given as keyword arguments are changed.

        :param int dlayer_index: Index of the dielectric layer to modify.

        Keyword arguments:

        :param float thickness: See [Son15]_ under BOX.
        :param float erel: See [Son15]_ under BOX.
        :param float mrel: See [Son15]_ under BOX.
        :param float eloss: See [Son15]_ under BOX.
        :param float mloss: See [Son15]_ under BOX.
        :param float esignma: See [Son15]_ under BOX.
        :param str name: See [Son15]_ under BOX.
        """

        if dlayer_index > len(self.project.geo.dlayers) - 1:
            raise self.error("Dlayer out of bound. Cannot set non-existing layer.")

        dlayer = self.project.geo.dlayers[dlayer_index]

        # Get keyword arguments from user input
        for key, value in kwargs.items():
            if key == "thickness":
                dlayer.thickness = value
            elif key == "erel":
                dlayer.erel = value
            elif key == "mrel":
                dlayer.mrel = value
            elif key == "eloss":
                dlayer.eloss = value
            elif key == "mloss":
                dlayer.mloss = value
            elif key == "esignma":
                dlayer.esignma = value
            elif key == "name":
                dlayer.name = value
            else:
                raise self.exception("Invalid keyword argument.")

    def setTlayer(self, tlayer_index, **kwargs):
        """
        Sets the parameters of a technology layer to those specified by the keyword arguments. Only parameters given as keyword arguments are changed.

        :param int tlayer_index: Index (gds stream number) of the technnology layer to modify.

        Keyword arguments:

        :param int dlayer_index: Index of the dielctric layer in which the technology layer reside.
        :param int to_dlayer_index: Index of the dielectric layer a via technology layer extends to. Only for via technology layers.
        :param str tlayer_type: The type of technology layer. Should be ``"metal"``, ``"via"`` or ``"brick"``. If a non-via layer is changed to via a value of ``to_dlayer_index`` should also be given.
        :param str name: Name of the technology layer.
        :param str brick_name: Name of the brick material. See [Son15]_ under BRI and BRA. Required if a brick tlayer is defined.
        :param bool lossless: Toggle for lossless metal.
        :param str filltype: Polygon filltype. Either ``"N"`` (staircase fill), ``"T"`` (diagonal fill) or ``"V"`` (conformal mesh). See [Son15]_ under NUM.
        :param str edgemesh: Either ``"Y"`` (on) or ``"N"`` (off). See [Son15]_ under NUM.
        :param str meshingfill: Either ``"RING"``, ``"CENTER"``, ``"VERTICES"``, ``"SOLID"`` or ``"BAR"``. See [Son15]_ under NUM.
        :param str pads: Either ``"NOCOVERS"`` or ``"COVERS"``. See [Son15]_ under NUM.
        """

        tlayerFound = False

        for dlayer in self.project.geo.dlayers:
            for tlayer in dlayer.tlayers:
                if tlayer.gds_stream == tlayer_index:
                    tlayerFound = True
                    for key, value in kwargs.items():
                        # Setting the layer type (lay_type)
                        if key == "tlayer_type":
                            if value in ["METAL", "metal"]:
                                tlayer.lay_type = value.upper()
                                tlayer.type = "MET POL"
                                for polygon in tlayer.polygons:
                                    polygon.type = tlayer.type
                            elif value in ["BRICK", "brick"]:
                                tlayer.lay_type = value.upper()
                                if "brick_name" not in kwargs.keys():
                                    raise self.exception("You must define a brick_name for brick type tech layers.")
                                brickFound = False
                                for brick in self.project.geo.bricks:
                                    if kwargs["brick_name"] == brick.name:
                                        brickFound = True
                                        tlayer.type = "BRI POL"
                                        tlayer.mtype = self.project.geo.bricks.index(brick) + 1
                                        for polygon in tlayer.polygons:
                                            polygon.type = tlayer.type
                                            polygon.mtype = tlayer.mtype
                                if not brickFound:
                                    raise NameError("Entered 'brick_name' not yet defined")
                            # Don't change anything if the layer is already VIA
                            elif value in ["VIA", "via"] and tlayer.lay_type == "VIA":
                                pass
                            # Request to_dlayer_index if the layer is changed to VIA
                            elif value in ["VIA", "via"] and tlayer.lay_type != "VIA":
                                if "to_dlayer_index" not in kwargs.keys():
                                    raise self.exception("You must specify to_dlayer_index.")
                                if kwargs["to_dlayer_index"] > len(self.project.geo.dlayers) - 1:
                                    raise self.exception("Out of bound value of to_dlayer_index.")
                                tlayer.lay_type = value.upper()
                                tlayer.type = "VIA POLYGON"
                                tlayer.to_level = kwargs["to_dlayer_index"]
                                for polygon in tlayer.polygons:
                                    polygon.type = tlayer.type
                                    polygon.to_level = tlayer.to_level
                            else:
                                raise self.exception("Invalid tlayer_type value.")
                        # If the tlayer is moved to a different dlayer, we
                        # also move the components (ports automatically follow)
                        elif key == "dlayer_index":
                            tlayer.ilevel = value
                            for polygon in tlayer.polygons:
                                polygon.ilevel = value
                            for component in dlayer.components:
                                component.levelnum = value
                                component.smdp1_levelnum = value
                                component.smdp2_levelnum = value
                        # Go on to the other parameters
                        elif key == "name":
                            tlayer.name = value
                        # mtype (metal type) is used to switch on lossless metal type
                        elif key == "lossless":
                            if value == True:
                                tlayer.mtype = -1
                                for polygon in tlayer.polygons:
                                    polygon.mtype = -1
                            elif value == False:
                                tlayer.mtype = 0
                                for polygon in tlayer.polygons:
                                    polygon.mtype = 0
                        elif key == "filltype":
                            tlayer.filltype = value
                            for polygon in tlayer.polygons:
                                polygon.filltype = value
                        elif key == "edgemesh":
                            tlayer.edgemesh = value
                            for polygon in tlayer.polygons:
                                polygon.edgemesh = value
                        # Only used for VIAs
                        elif key == "meshingfill":
                            tlayer.meshingfill = value
                            for polygon in tlayer.polygons:
                                polygon.meshingfill = value
                        # Only used for VIAs
                        elif key == "pads":
                            tlayer.pads = value
                            for polygon in tlayer.polygons:
                                polygon.pads = value
                        # Handled with lay_type
                        elif key == "to_dlayer_index":
                            pass
                        elif key == "brick_name":
                            pass
                        else:
                            raise self.exception("Invalid keyword argument.")

        if tlayerFound == False:
            raise self.exception("Tlayer not found.")

    def addBrick(self, erel=1, loss_tan=0, cond=0, name="Air"):
        """
        Adds a dielectric layer to the project.

        :param erel: relative permitivity or [erelx, erely, erelz]
	:type erel: float or list of floats of length 3
        :param loss_tan: loss tangent or [erelx, erely, erelz]
	:type loss_tan: float or list of floats of length 3
        :param cond: conductivity or [erelx, erely, erelz]
	:type cond: float or list of floats of length 3

        """

        # Check to see if inputs are floats or lists of floats with length three
        try:
            if not len(erel) == 3:
                raise self.exception("erel is not either a float or a list of floats length three")
            else:
                for x in range(3):
                    if not isinstance(erel[x], float) and not isinstance(erel[x], int):
                        raise self.exception("erel is not either a float or a list of floats length three")
        except TypeError:
            if not isinstance(erel, float) and not isinstance(erel, int):
                raise self.exception("erel is not either a float or a list of floats length three")
            pass
        try:
            if not len(loss_tan) == 3:
                raise self.exception("loss_tan is not either a float or a list of floats length three")
            else:
                for x in range(3):
                    if not isinstance(loss_tan[x], float) and not isinstance(loss_tan[x], int):
                        raise self.exception("loss_tan is not either a float or a list of floats length three")
        except TypeError:
            if not isinstance(loss_tan, float) and not isinstance(loss_tan, int):
                raise self.exception("loss_tan is not either a float or a list of floats length three")
            pass
        try:
            if not len(cond) == 3:
                raise self.exception("cond is not either a float or a list of floats length three")
            else:
                for x in range(3):
                    if not isinstance(cond[x], float) and not isinstance(cond[x], int):
                        raise self.exception("cond is not either a float or a list of floats length three")
        except TypeError:
            if not isinstance(cond, float) and not isinstance(cond, int):
                raise self.exception("cond is not either a float or a list of floats length three")
            pass

        newBrick = Brick()

        if not isinstance(erel, list) and not isinstance(loss_tan, list) and not isinstance(cond, list):
            newBrick.values = [erel, loss_tan, cond]  # Brick class default to isotropic
        else:
            newBrick.isIsotropic = False
            params = []
            for val in [erel, loss_tan, cond]:
                if not isinstance(val, list):
                    params.append([val, val, val])
                else:
                    params.append(val)
            newBrick.values = [params[j][i] for i in range(3) for j in range(3)]  # Order values for sonnet syntax
        newBrick.name = name
        self.project.geo.bricks.append(newBrick)


    ########################################################################
    # FREQUENCY AND PARAMETER SWEEPS                                       #
    ########################################################################

    def setFrequencySweep(self, f1=5, f2=8, fstep=None):
        """
        Sets the frequency sweep to be run during the simulation.

        :param float f1: Minimum frequency in the sweep.
        :param float f2: Maximum frequency in the sweep.
        :param fstep: The stepsize in a linear frequency sweep. If set to ``None`` an adaptive frequency sweep will run.
        :type fstep: None or float
        """

        # Technical description for delevopers:
        # Redefines or adds the FREQ block with a single frequency sweep, and
        # sets this sweep as the current sweep in the CONTROL block
        # Currently, the following sweep types are implemented:
        # SIMPLE: Linear sweep from f1 to f2 in steps fstep if fstep is speficied
        # ABS: Adaptive sweep from f1 to f2 if fstep is left unspecified (None)

        freq = Freq()
        freq.f1 = f1
        freq.f2 = f2

        if fstep == None:
            freq.sweep = "ABS"
        elif fstep > 0 and fstep < abs(f1 - f2):
            freq.sweep = "SIMPLE"
            freq.fstep = fstep
        else:
            raise self.exception("Invalid value of fstep.")

        if f1 >= f2:
            raise self.exception("Invalid frequency sweep.")

        self.project.freq = freq

        # Switch on the frequency sweep in the CONTROL block
        if self.project.control == None:
            control = Control()
        else:
            control = self.project.control

        control.sweep = freq.sweep
        self.project.control = control

    def addParameter(self, parameter, unittype=None, **kwargs):
        """
        Adds a variable parameter to the project.

        :param str parameter: Name of the parameter. If the name of an existing ideal component is given, the variable will be associated to that component's value.
        :param str unittype: The unit type of the variable. See [Son15]_ under VALVAR. If ``parameter`` is the name of an existing ideal component, the unit type will be inherited from the component.

        Keyword arguments:

        :param float value: The value of the parameter. Default is 30. If ``parameter`` is the name of an existing component, the value will be inherited from the component.
        :param str description: Description of the parameter. Default is empty quotes, ``""``.
        """

        # Technical description for delevopers:
        # Adds a variable parameter to the VALVAR block

        valvar = Valvar()
        valvar.varname = parameter
        valvar.unittype = unittype

        for key, value in kwargs.items():
            if key == "value":
                valvar.value = value
            elif key == "description":
                valvar.description = value
            else:
                raise self.exception("Invalid keyword argument.")

        # If the parameter is the name of a component, we grab the unittype
        # and set the component's value to the new variable parameter
        for dlayer in self.project.geo.dlayers:
             for component in dlayer.components:
                 if component.label == parameter:
                     valvar.unittype = component.idealtype
                     component.compval = parameter

        if valvar.unittype != None:
            valvar.unittype = valvar.unittype.upper()
        else:
            raise self.exception("You have to specify unittype if the parameter is not an existing component.")

        self.project.geo.valvars.append(valvar)

    def addParameterSweep(self, parameter, pmin, pmax, pstep, **kwargs):
        """
        Adds a parameter sweep to the project. Unless the keyword argument ``to_existing_sweep`` is given any previously set parameter sweeps will be overwritten. You can see the active sweeps set up in the project by running :func:`printParameters()`. The parameter sweep runs within a given frequency sweep, either previously set with :func:`setFrequencySweep` or given with keyword arguments. If no frequency sweep has been defined for the project, the default from :func:`setFrequencySweep` will be set.

        :param str parameter: Name of the parameter to sweep. It must be the name of an existing parameter, for instance defined by :func:`addParameter`.
        :param float pmin: Minimum parameter value in the sweep.
        :param float pmax: Maximum parameter value in the sweep.
        :param pstep: The stepsize in a linear sweep. If set to ``None`` an adaptive sweep will run.
        :type pstep: None or float

        Keyword arguments:

        :param int to_existing_sweep: Index of an existing parameter sweep (1, 2, ect.). If given the parameter sweep is added to the existing parameter sweep such that several parameters will be sweept during the simulation.
        :param str ytype: Type of sweep. Either ``"N"``, ``"Y"``, ``"YN"``, ``"YC"``, ``"YS"``, or ``"YE"``. See [Son15]_ under VARSWP.
        :param float f1: Minimum frequency in the sweep.
        :param float f2: Maximum frequency in the sweep.
        :param fstep: The stepsize in a linear frequency sweep. If set to ``None`` an adaptive frequency sweep will run.
        :type fstep: None or float
        """

        # Technical description for developers:
        # Adds a parameter sweep, where "parameter" must be the name of a
        # parameter in the VALVAR block.
        # By default a new sweep is created with a single parameter being
        # sweeped (from pmin to pmax in steps of pstep). The frequency
        # sweep for the new sweep is set by the keyword arguments f1, f2
        # and fstep (linear if fstep is given, otherwise adaptive). If no
        # frequency sweep is given, we use the frequency from the FREQ
        # block if it exists, otherwise we use a default adaptive sweep.
        # If the argument to_existing_sweep is given (an integer within the
        # number of existing parameter sweeps), we add the given parameter
        # sweep to the existing sweep (such that more than one parameter
        # will be swept). Any frequency parameters will overwrite the
        # frequency settings for the existing sweep.

        var = Var()
        var.min = pmin
        var.max = pmax
        var.step = pstep
        if parameter not in [valvar.varname for valvar in self.project.geo.valvars]:
            raise self.exception("Parameter does not exist. Use printParameters() to see defined parameters, and use addParameter(parameter) to add a new one.")
        var.parameter = parameter

        # Add to an existing sweep if to_existing_sweep is given
        if "to_existing_sweep" in kwargs.keys():
            value = kwargs["to_existing_sweep"]
            if value not in range(1, len(self.project.varswp.psweeps) + 1):
                raise self.exception("Invalid value of to_existing_sweep.")
            else:
                psweep = self.project.varswp.psweeps[value - 1]
                psweep.vars.append(var)
        # If not we create a new single parameter sweep
        else:
            psweep = Psweep()
            psweep.vars = [var]
            if self.project.varswp == None:
                self.project.varswp = Varswp()
            self.project.varswp.psweeps.append(psweep)

        # Copy the frequency sweep from the FREQ block
        if self.project.freq != None:
            psweep.f1 = self.project.freq.f1
            psweep.f2 = self.project.freq.f2
            if self.project.freq.fstep != None:
                psweep.fstep = self.project.freq.fstep
                psweep.sweeptype = "SWEEP"

        # Overwrite the frequency sweep if it is given
        for key, value in kwargs.items():
            if key == "ytype" and value in ["N", "Y", "YN", "YC", "YS", "YE"]:
                var.ytype = value
            elif key == "f1":
                psweep.f1 = value
            elif key == "f2":
                psweep.f2 = value
            elif key == "fstep":
                # If fstep is given, we use linear sweep (SWEEP), otherwise
                # we use the default adaptive sweep (ABS_ENTRY)
                psweep.fstep = value
                psweep.sweeptype = "SWEEP"
            elif key == "to_existing_sweep":
                pass
            else:
                raise self.exception("Invalid keyword argument.")

        # Sanity check of the frequency sweep
        if psweep.f1 != None and psweep.f2 != None:
            if psweep.f1 >= psweep.f2:
                raise self.exception("Invalid frequency sweep.")
        if psweep.fstep != None:
            if not (psweep.fstep > 0 and psweep.fstep < abs(psweep.f1 - psweep.f2)):
                raise self.exception("Invalid value of fstep.")

        # Switch on the parameter sweep in the CONTROL block
        if self.project.control == None:
            control = Control()
        else:
            control = self.project.control

        control.sweep = "VARSWP"
        self.project.control = control

    ########################################################################
    # OUTPUT DATA                                                          #
    ########################################################################

    def setOutput(self, **kwargs):
        """
        Sets an output file for simulation data. By default a single spreadsheet file (.csv) is created with the same filename as the Sonnet project file. By default the data format is S-parameters given in dB and angles. See [Son15]_ under FILEOUT for other options.

        Keyword arguments:

        :param str filetype: See [Son15]_ under FILEOUT. Default is ``"CSV"``.
        :param str embed: See [Son15]_ under FILEOUT. Default is ``"D"``.
        :param str abs_inc: See [Son15]_ under FILEOUT. Default is ``"Y"``.
        :param str filename: See [Son15]_ under FILEOUT. Default is ``"$BASENAME.csv"``.
        :param str comments: See [Son15]_ under FILEOUT. Default is ``"NC"``.
        :param int sig: See [Son15]_ under FILEOUT. Default is ``8``.
        :param str partype: See [Son15]_ under FILEOUT. Default is ``"S"``.
        :param str parform: See [Son15]_ under FILEOUT. Default is ``"DB"``.
        :param str ports: See [Son15]_ under FILEOUT. Default is ``"R 50"``.
        :param str folder: See [Son15]_ under FOLDER. Default is ``None``.
        """

        # Only a geometry project output file of "Response" type is implemeted.

        fileout = Fileout()

        # Get keyword arguments from user input
        for key, value in kwargs.items():
            if key == "filetype":
                fileout.filetype = value
            elif key == "embed":
                fileout.embed = value
            elif key == "abs_inc":
                fileout.abs_inc = value
            elif key == "filename":
                fileout.filename = value
            elif key == "comments":
                fileout.comments = value
            elif key == "sig":
                fileout.sig = value
            elif key == "partype":
                fileout.partype = value
            elif key == "parform":
                fileout.parform = value
            elif key == "ports":
                fileout.ports = value
            elif key == "folder":
                fileout.folder = value
            else:
                raise self.exception("Invalid keyword argument.")

        # Overwrite any previous fileout settings
        self.project.fileout = fileout

    def getOutput(self, data="frequency", run=1):
        """
        Returns a list of data from the data resulting created after a Sonnet simulation. It is assumed that the data file is a .csv file, which is the default setting when running :func:`setOutput`. This function makes it easy to extract simulation data and plot it within Python.

        :param str data: String specifying the data. It must follow the naming in the .csv file, for instance ``"MAG[S12]"`` for the magnitude of the S12-parameter. The default is frequency data.
        :param int run: The sweep number if a parameter was swept during the simulation.

        :returns: List of data.
        """

        # Verify that the data file exists
        file_found = 0
        for root, dirs, files in os.walk(self.data_file_path):
            for file in files:
                # Make search case insensitive
                if self.data_file.lower() == file.lower():
                    file_found = 1

        if (file_found == 0):
            print("Project file %s can not be located in path %s"%(self.data_file,self.data_file_path))
            raise self.exception("Data file not found! Check that directory and filename are correct!")

        with open(self.data_file_path + self.data_file, 'r') as fd:
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

            # Skip all lines containing "=", i.e. parameter sweep lines
            line = fd.readline()
            while "=" in line:
                line = fd.readline()

            # Collect plot data from the data block
            datalist = []
            while line != "" and line[0] != "!":
                try:
                    datalist.append(float(line.split(",")[index]))
                except:
                    datalist.append(float(line.split()[index]))
                line = fd.readline()

            return datalist

    ########################################################################
    # SONNET SIMULATOR (em.exe, emstatus.exe)                              #
    ########################################################################

    def runSimulation(self):
        """
        Runs the Sonnet simulation without the pop-up status monitor. This function also calls :func:`printProject()`, thereby saving any changes made in SonPy to the Sonnet project file before starting the simulation.
        """

        # Print the Sonnet Project File
        self.printProject()

        if self.done_flag == 0:
            print("Can't start new simulation until previous simulation completes.")
            return

        # Verify Sonnet project file exists
        file_found = 0
        for root, dirs, files in os.walk(self.sonnet_file_path):
            for file in files:
                # Make search case insensitive
                if self.sonnet_file.lower() == file.lower():
                    file_found = 1

        if file_found == 0:
            print("Project file {:s} can not be located in path {:s}".format(self.sonnet_file, self.sonnet_file_path))
            raise self.exception("Sonnet project file not found! Check that directory and filename are correct!")

        self.done_flag = 0
        args = ([self.executable_path + self.executable_file, # command
                 self.sonnet_options, # options
                 self.sonnet_file_path + self.sonnet_file]) # file

        try:
            self.em_process = subprocess.Popen(args, stdout=subprocess.PIPE)
            self.run_count = self.run_count + 1
        except:
            print("Error! Can't start process, use setSonnetInstallationPath(path) to point the class to the location of your em.exe file")
            print("Current path is {:s}".format(self.executable_path))
            self.done_flag = 1
            raise self.exception("Can not run sonnet executable file, file not found")

        # Wait for the process to complete
        self.em_process.wait()

    def runSimulationStatusMonitor(self):
        """
        Runs the Sonnet simulation with the pop-up status monitor. This function also calls :func:`printProject()`, thereby saving any changes made in SonPy to the Sonnet project file before starting the simulation.
        """

        # Print the Sonnet Project File
        self.printProject()

        if self.done_flag == 0:
            print("Can't start new simulation until previous simulation completes.")
            return

        # Verify Sonnet project file exists
        file_found = 0
        for root, dirs, files in os.walk(self.sonnet_file_path):
            for file in files:
                # Make search case insensitive
                if self.sonnet_file.lower() == file.lower():
                    file_found = 1

        if file_found == 0:
            raise self.exception("Sonnet project file {:s} can not be located in path {:s}".format(self.sonnet_file, self.sonnet_file_path))

        self.done_flag = 0
        args = ([self.executable_path + self.executable_and_monitor_file, # command
              self.executable_and_monitor_options, # options
              self.sonnet_file_path + self.sonnet_file]) # file
        try:
            self.emstatus_process = subprocess.Popen(args, stdout=subprocess.PIPE)
            self.run_count = self.run_count + 1
        except:
            print("Error! Can't start process, use setSonnetInstallationPath(path) to point the class to the location of your em.exe file")
            print("Current path is {:s}".format(self.executable_path))
            self.done_flag = 1
            raise self.exception("Can not run sonnet executable file, file not found")
        time.sleep(5)
        self.getEmProcessID()

        # Wait for the process to complete
        self.emstatus_process.wait()

    def getEmProcessID(self):
        # Internal use only.

        # Based on SimulationStatusMonitor process 'emstatus.exe', find out child process 'em.exe'
	if OS == 'Windows':
		WMI = GetObject('winmgmts:')
		processes = WMI.InstancesOf('Win32_Process')
		self.parentPID = int(self.emstatus_process.pid)
		self.emPID = None
		for process in processes:
		    parent = int(process.Properties_('ParentProcessId').Value)
		    child = int(process.Properties_('ProcessId').Value)
		    if (parent == self.parentPID):
			self.emPID = child
			break
	elif OS == 'Linux':
		self.parentPID = int(self.emstatus_process.pid)
        	child = os.popen(f'pgrep -P {self.parentPID}').read()
        	child = ''.join([c for c in child if c.isdigit()])
        	self.emPID = int(child)
		

    ########################################################################
    # MISCELLANEOUS FUNCTIONS                                              #
    ########################################################################

    def addComment(self, string):
        """
        Adds a comment to the top of the Sonnet project file.

        :param str string: Comment.
        """

        # Comments in Sonnet project files start with "!"
        self.project.preheader.insert(0, "! {:s}\n".format(string))

    def runMakeover(self):
        """
        Applies a series of other functions. This makeover function takes a GDSII file, runs it through a series of standardized tasks such that the project after the makeover is ready for adding ports, applying other specific settings and simulation.

        The following operations are applied:

        1. :func:`runGdsTranslator()`: Translate the GDSII file and read the project into SonPy.
        2. Set the bottom dielectric layer to Silicon with the appropriate parameters.

        Depending on the number of technology layers, we either create an air bridge, or we do not.

        3. If there is only one technology layer (assumed to have gds stream 23), there is no air bridge, and the top layer is set to vacuum. The technology layer is set to lossless metal.

        3. If there are three technology layers (assumed to have gds streams 23, 50 and 51), we create an air bridge from 50 (the top) and 51 (set to a via for bridge pillars). All technology layers are set to lossless metal. The top dielectric layer is made a thin vacuum at the bridge pillar level, and a new thick vacuum layer is added on top of the substrate.

        4. :func:`setFrequencySweep()`: The default frequency sweep is set.

        5. :func:`setOutput()`: The default output data file is set.

        """

        # Applies a series of functions that takes to gds file into a
        # Sonnet file ready for adding ports and simulation

        # Convert .gds to .son
        self.runGdsTranslator()

        # Add comment
        self.addComment("SonPy: The EQuS custom makeover has been performed")

        # Set the bottom layer to silicon
        self.setDlayer(1, thickness=279,\
                          erel=11.45,\
                          mrel=1,\
                          eloss=1e-006,\
                          mloss=0,\
                          esignma=0.00044,\
                          name="Silicon (EQuS)")

        # One tlayer means there should be no air bridges
        if len(self.project.geo.dlayers[0].tlayers) == 1:
            # Set the top layer to vacuum
            self.setDlayer(0, thickness=500,\
                              erel=1,\
                              mrel=1,\
                              eloss=0,\
                              mloss=0,\
                              esignma=0,\
                              name="Vacuum")
            # Set the tlayer (assumed gds_stream = 23) to lossless metal
            self.setTlayer(23, lossless=True)

        # Three tlayers means we make an air bridge
        elif len(self.project.geo.dlayers[0].tlayers) == 3:
            # Set a thin vacuum layer
            self.setDlayer(0, thickness=2.9,\
                              erel=1,\
                              mrel=1,\
                              eloss=0,\
                              mloss=0,\
                              esignma=0,\
                              name="Vacuum")
            # Add a thick vacuum layer on top
            self.addDlayer(thickness=500,\
                           erel=1,\
                           mrel=1,\
                           eloss=0,\
                           mloss=0,\
                           esignma=0,\
                           name="Vacuum")
            # Set the tlayer (assumed gds_stream = 23) to lossless metal
            self.setTlayer(23, lossless=True)
            # Set the remaining two tlayers to the air bridge
            self.setTlayer(50, dlayer_index=0, lossless=True) # top of bridge
            self.setTlayer(51, to_dlayer_index=0, lossless=True, tlayer_type="via") # via (bridge pillars)

        else:
            raise self.exception("Unexpected number of technology layers.")

        # Set a default frequency sweep
        self.setFrequencySweep()

        # Set a default output file
        self.setOutput()


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


The following is the result of running em.exe and gds.exe from the Command Line
with the option -h. Notice that emgraph.exe and emgraph.exe does not have -h options.

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
