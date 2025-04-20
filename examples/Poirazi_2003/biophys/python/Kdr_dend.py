# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class Kdr_dend(IonChannel):
    """
    Kdr
    """

    def __init__(self, name="Kdr_dend"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0
            }
        self.range_params = {
            "gbar": 0
            }
        self.states = {
            "n": 0.0
            }
        self._state_powers = {
            "n": {'power': 2}
            }
        self.ion = "k"
        self.current_name = "i_k"
        self.current_available = False
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        
        nInf = 1 / (1 + np.exp(((v + 42) / -2)))
        nTau = 2.2
        return nInf, nTau
    
    