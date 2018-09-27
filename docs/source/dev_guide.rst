Developer's guide
=================

.. note::
    This section can be skipped by regular users.

Sonnet project file syntax
--------------------------

To understand how SonPy is written it is crucial to understand the syntax of Sonnet project files (.son files) as explained in the manual [Son15]_. Opening a Sonnet project file in a text editor makes it readable by humans. It is composed of a series of blocks that begins with a ``BLOCKNAME`` line and ends with a ``BLOCKNAME END`` line. Each block defines different properties of the Sonnet project, for instance the DIM block specifies the physical units, the GEO block sets the metal properties and defines all the polygons that make up the circuit, and the FREQ block sets the frequency sweep used in the simulation. Within each block are statements that defines every aspect of the project. SonPy does not implement all of the possibilities within Sonnet (that would be crazy!). Only those functionalities that where valuable to the EQuS Group at MIT at the time of development were implemented, but this guide should make it easier for you to implement your own features.

SonPy is comprised by classes and functions defined in ``sonpy.py``. The functions fall into three categories:

1. Functions that runs a Sonnet subprogram (em.exe, emstatus.exe or gds.exe) found in Sonnet's program folder. They can be run from the command line, and SonPy runs them as a subprocess. These functions are used to convert a GDSII file to a Sonnet project file or to run the simulation.
2. Functions that manipulate the Sonnet project. They are used to add ports, change metal properties, set up the simulation ect.
3. Miscellaneous functions such as for reading or printing Sonnet project files (typically not necessary to run explicitly), reading output files from a Sonnet simulation, or printing information about the current project in the command line.

Python class structure for a Sonnet project
-------------------------------------------

A Sonnet project in SonPy is an instance of the :class:`sonnet` class. The instance variables of the ``sonnet`` class stores all the information needed for Python and Sonnet to interact, such as file paths to the Sonnet programs, Sonnet project file, GDSII file, data output file ect. The Sonnet project itself (equivalent to a Sonnet project file) is contained in the instance variable ``project``, which is initialized as an instance of the ``Project`` class. The ``Project`` class mimics the structure of a Sonnet project file (compare with p. 8 of [Son15]_)::

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

Each instance variable (except ``preheader``) corresponds to a Sonnet project file block. They are all classes themselves containing stuff belonging to that block. For instance, for the GEO block SonPy has a class ``Geo`` intented to be stored as the ``geo`` instance variable in the ``Project`` class::

    class Geo():
        def __init__(self):
            self.tmet = None
            self.bmet = None
            self.met = None
            self.box = None
            self.dlayers = []
            self.valvars = []
            self.lorgn = None
            self.npoly = None

Depending on the purpose, the instance variables of the ``Geo`` class may be a class, list of classes or a simply type like an integer. For instance, ``box`` is intended to be initialized as an instance of the ``Box`` class to store the data from the BOX statement (p. 33 of [Son15]_)::

    class Box():
        def __init__(self):
            self.nlev = None
            self.xwidth = None
            self.ywidth = None
            self.xcells2 = None
            self.ycells2 = None
            self.nsubs = None
            self.eeff = None

Since each project only contains a single BOX statement, it is sufficient to only make room for one in the Python class. However, there may be any number of dielectric layers in the project, and so ``dlayers`` is intended to store a list of instances of the ``Dlayer`` class, each instance containing the data of a single layer. Lastly, some information can be saved as just a number, like ``npoly`` from the NUM statement (p. 43 of [Son15]_) which specify the number of polygons in the project.

Reading a Sonnet project into SonPy
-----------------------------------

Given a Sonnet project file (like the output of a .gds to .son conversion), SonPy must read and store the Sonnet project. This is done with the function ``readProject`` which creates an instance of ``Project`` (called ``project`` stored in ``self.project``) and carefully goes through the Sonnet project file line by line. The Sonnet project is then stored in the detailed class structure of ``Project`` and its instance variables. For instance, when the line ``BEGIN GEO`` is read in the Sonnet project file, the class ``Geo`` is initialized and assigned to ``self.project.geo``. While looking through the GEO block we will for instance recognize the BOX statement (p. 33 of [Son15]_) which defines some physical parameters of the circuit. SonPy has a corresponding ``Box`` class with the physical parameters as instance variables. The parameter names in SonPy (``nlev``, ``xwidth``, ``ywidth`` ect.) are always inherited from the Sonnet project file syntax whenever possible. To see exactly which Sonnet project file parameters are stored as which SonPy parameters, you will have to look into the workings of the ``readProject`` function, and compare with the Sonnet project file syntax in [Son15]_. An instance of ``Box`` is initialized with the parameters read from the Sonnet project file, and the ``Box`` instance is saved as ``self.project.geo.box``. The BOX parameters can then be retrieved as ``self.project.geo.box.nlev`` for the integer parameters ``nlev`` which specify the number of layer levels in the project. In this way the Sonnet project is stored as a Russian doll, and every parameter of the project is accessible to SonPy.

Notice that the function ``runGdsTranslator`` also runs ``readProject``, so when converting a GDSII file with ``runGdsTranslator`` the Sonnet project is automatically read into SonPy.

Manipulating the Sonnet project
-------------------------------

When ``readProject`` has run, the entire Sonnet project is accessible to SonPy. Most of the functions in SonPy are dedicated to add, remove of alter stuff in the Sonnet project. For instance, the function ``removeDlayer`` removes a dielectric layer by removing the appropriate member from the list ``self.project.geo.dlayers`` of ``Dlayer`` class instances. The layer indices of the layers below the removed layer are updated (including everything that reside in those layers such as technology layers, ports and components). Finally the variable ``nlev`` which holds the number of dielectric layers is decresed by one with the line ``self.project.geo.box.nlev += -1``. All manipulations of the Sonnet project is done by altering ``Project`` class instance ``self.project``.

Before you add new functions of your own to SonPy, familiarize yourself with the code of the existing functions. Often the structures appear in different functions, for instance looping over all ports in all dielectric layers, or looping over all polygons in all technology layers in all dielectric layers, and you can straightforward copy or slightly alter existing code blocks. This also preserves consistency in coding style.

Updating the Sonnet project file
--------------------------------

When all the appropriate changes had been made to the Sonnet project, and it is time to simulate the project, a new Sonnet project file must be created. This is done by the function ``printProject`` which overwrites the Sonnet project file with the modified project. It goes through all the data stored in ``self.project`` and writes the appropriate statements to the .son file following the Sonnet project file syntax.

Notice that the functions ``runSimulation`` and ``runSimulationStatusMonitor`` (both starting a Sonnet simulation) also calls ``printProject``, so when running a simulation using these functions there is no need to explicitly run ``printProject``.
