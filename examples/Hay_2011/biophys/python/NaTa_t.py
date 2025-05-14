# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class NaTa_t(IonChannel):
    """
    
    """

    def __init__(self, name="NaTa_t"):
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
            "m": {'power': 3},
            "h": {'power': 1}
            }
        self.ion = "na"
        self.current_name = "i_na"
        self.current_available = False
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        
        qt = 2.3 ** ((34 - 21) / 10)
        conditions = [v == -38, ~(v == -38)]
        choices = [v + 0.0001, v]
        v = np.select(conditions, choices)
        mAlpha = (0.182 * (v - -38)) / (1 - np.exp((-(v - -38) / 6)))
        mBeta = (0.124 * (-v - 38)) / (1 - np.exp((-(-v - 38) / 6)))
        mTau = (1 / (mAlpha + mBeta)) / qt
        mInf = mAlpha / (mAlpha + mBeta)
        conditions = [v == -66, ~(v == -66)]
        choices = [v + 0.0001, v]
        v = np.select(conditions, choices)
        hAlpha = (-0.015 * (v - -66)) / (1 - np.exp(((v - -66) / 6)))
        hBeta = (-0.015 * (-v - 66)) / (1 - np.exp(((-v - 66) / 6)))
        hTau = (1 / (hAlpha + hBeta)) / qt
        hInf = hAlpha / (hAlpha + hBeta)
        return mInf, mTau, hInf, hTau
    
    