# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.membrane.mechanisms import IonChannel
import numpy as np

class Nap_Et2(IonChannel):
    """
    
    """

    def __init__(self, name="Nap_Et2"):
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
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self):
        
        qt = 2.3 ** ((34 - 21) / 10)
        mInf = 1.0 / (1 + np.exp(((v - -52.6) / -4.6)))
        conditions = [v == -38, ~(v == -38)]
        choices = [v + 0.0001, v]
        v = np.select(conditions, choices)
        mAlpha = (0.182 * (v - -38)) / (1 - np.exp((-(v - -38) / 6)))
        mBeta = (0.124 * (-v - 38)) / (1 - np.exp((-(-v - 38) / 6)))
        mTau = (6 * (1 / (mAlpha + mBeta))) / qt
        conditions = [v == -17, ~(v == -17)]
        choices = [v + 0.0001, v]
        v = np.select(conditions, choices)
        conditions = [v == -64.4, ~(v == -64.4)]
        choices = [v + 0.0001, v]
        v = np.select(conditions, choices)
        hInf = 1.0 / (1 + np.exp(((v - -48.8) / 10)))
        hAlpha = (-2.88e-06 * (v + 17)) / (1 - np.exp(((v + 17) / 4.63)))
        hBeta = (6.94e-06 * (v + 64.4)) / (1 - np.exp((-(v + 64.4) / 2.63)))
        hTau = (1 / (hAlpha + hBeta)) / qt
        return mInf, mTau, hInf, hTau
    
    