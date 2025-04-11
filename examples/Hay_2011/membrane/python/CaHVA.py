# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class CaHVA(IonChannel):
    """
    
    """

    def __init__(self, name="CaHVA"):
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
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self):
        
        conditions = [v == -27, ~(v == -27)]
        choices = [v + 0.0001, v]
        v = np.select(conditions, choices)
        mAlpha = (0.055 * (-27 - v)) / (np.exp(((-27 - v) / 3.8)) - 1)
        mBeta = 0.94 * np.exp(((-75 - v) / 17))
        mInf = mAlpha / (mAlpha + mBeta)
        mTau = 1 / (mAlpha + mBeta)
        hAlpha = 0.000457 * np.exp(((-13 - v) / 50))
        hBeta = 0.0065 / (np.exp(((-v - 15) / 28)) + 1)
        hInf = hAlpha / (hAlpha + hBeta)
        hTau = 1 / (hAlpha + hBeta)
        return mInf, mTau, hInf, hTau
    
    