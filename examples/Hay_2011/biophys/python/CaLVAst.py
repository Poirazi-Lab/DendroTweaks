# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class CaLVAst(IonChannel):
    """
    
    """

    def __init__(self, name="CaLVAst"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0
            }
        self.range_params = {
            "gbar": 0.0
            }
        self.states = {
            "m": 0.0,
            "h": 0.0
            }
        self._state_powers = {
            "m": {'power': 2},
            "h": {'power': 1}
            }
        self.ion = "ca"
        self.current_name = "i_ca"
        self.current_available = False
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self):
        
        qt = 2.3 ** ((34 - 21) / 10)
        v = v + 10
        mInf = 1.0 / (1 + np.exp(((v - -30.0) / -6)))
        mTau = (5.0 + (20.0 / (1 + np.exp(((v - -25.0) / 5))))) / qt
        hInf = 1.0 / (1 + np.exp(((v - -80.0) / 6.4)))
        hTau = (20.0 + (50.0 / (1 + np.exp(((v - -40.0) / 7))))) / qt
        v = v - 10
        return mInf, mTau, hInf, hTau
    
    