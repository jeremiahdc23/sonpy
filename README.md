# SonPy

_Python interface for Sonnet._

SonPy is a Python module that lets the user manipulate and simulate Sonnet Software projects through Python. Please see the documentation in SonPy.pdf for more information.

## Changelog

**Version 1.1 (2018-09-16)**

Functionality to handle brick layers added.

* added self.bricks = [] to Geo class
* added Brick class
* added section to readProject to initialize BRI and BRA definitions
* added section to printProject to print BRI and BRA material initiations
* added parameter to setTlayer to match defined brick to brick material
* made necessary additions to set tlayer parameters appropriate if brick material defined
* wrote addBrick function which takes in erel, loss_tan, cond, and brick name
