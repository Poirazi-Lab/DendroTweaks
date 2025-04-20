# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class calH(IonChannel):
    """
    Ca L-type channel with high treshold of activation
    """

    def __init__(self, name="calH"):
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
        self.current_available = True
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        
        mInf = 1 / (1 + np.exp(((v + 37) / -1)))
        hInf = 1 / (1 + np.exp(((v + 41) / 0.5)))
        mTau = 3.6
        hTau = 29
        return mInf, mTau, hInf, hTau
    
    