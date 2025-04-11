# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class nap(IonChannel):
    """
    Na persistent channel
    """

    def __init__(self, name="nap"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0,
            "K": 4.5,
            "vhalf": -50.4
            }
        self.range_params = {
            "gbar": 0,
            "K": 4.5,
            "vhalf": -50.4
            }
        self.states = {
            "n": 0.0
            }
        self._state_powers = {
            "n": {'power': 3}
            }
        self.ion = "na"
        self.current_name = "i_na"
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        K = self.params["K"]
        vhalf = self.params["vhalf"]
        
        nInf = 1 / (1 + np.exp(((vhalf - v) / K)))
        nTau = 1
        return nInf, nTau
    
    