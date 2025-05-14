# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class K_Tst(IonChannel):
    """
    
    """

    def __init__(self, name="K_Tst"):
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
            "m": {'power': 1},
            "h": {'power': 1}
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
        
        qt = 2.3 ** ((34 - 21) / 10)
        v = v + 10
        mInf = 1 / (1 + np.exp((-(v + 0) / 19)))
        mTau = (0.34 + (0.92 * np.exp((-((v + 71) / 59) ** 2)))) / qt
        hInf = 1 / (1 + np.exp((-(v + 66) / -10)))
        hTau = (8 + (49 * np.exp((-((v + 73) / 23) ** 2)))) / qt
        v = v - 10
        return mInf, mTau, hInf, hTau
    
    