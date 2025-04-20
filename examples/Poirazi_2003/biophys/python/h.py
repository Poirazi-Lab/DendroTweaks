# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class h(IonChannel):
    """
    H-current that uses Na ions
    """

    def __init__(self, name="h"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "e": -10,
            "K": 8.5,
            "vhalf": -90
            }
        self.range_params = {
            "gbar": 0.0,
            "e": -10,
            "K": 8.5,
            "vhalf": -90
            }
        self.states = {
            "n": 0.0
            }
        self._state_powers = {
            "n": {'power': 1}
            }
        self.ion = "None"
        self.current_name = "i_None"
        self.current_available = True
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        K = self.params["K"]
        vhalf = self.params["vhalf"]
        
        nInf = 1 - (1 / (1 + np.exp(((vhalf - v) / K))))
        conditions = [v > -30, ~(v > -30)]
        choices = [1, 2 * ((1 / (np.exp(((v + 145) / -17.5)) + np.exp(((v + 16.8) / 16.5)))) + 5)]
        nTau = np.select(conditions, choices)
        return nInf, nTau
    
    