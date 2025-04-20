# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class SKv3_1(IonChannel):
    """
    
    """

    def __init__(self, name="SKv3_1"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0
            }
        self.range_params = {
            "gbar": 0.0
            }
        self.states = {
            "m": 0.0
            }
        self._state_powers = {
            "m": {'power': 1}
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

    
    def compute_kinetic_variables(self):
        
        mInf = 1 / (1 + np.exp(((v - 18.7) / -9.7)))
        mTau = (0.2 * 20.0) / (1 + np.exp(((v - -46.56) / -44.14)))
        return mInf, mTau
    
    