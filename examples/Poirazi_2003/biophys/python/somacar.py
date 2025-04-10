# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class somacar(IonChannel):
    """
    Ca R-type channel with medium threshold for activation
    """

    def __init__(self, name="somacar"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0
            }
        self.range_params = {
            "gbar": 0
            }
        self.states = {
            "m": 0.0,
            "h": 0.0
            }
        self._state_powers = {
            "m": {'power': 3},
            "h": {'power': 1}
            }
        self.ion = "ca"
        self.current_name = "i_ca"
        self.independent_var_name = "cai"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        
        mInf = 1 / (1 + np.exp(((v + 60) / -3)))
        hInf = 1 / (1 + np.exp(((v + 62) / 1)))
        mTau = 100
        hTau = 5
        return mInf, mTau, hInf, hTau
    
    