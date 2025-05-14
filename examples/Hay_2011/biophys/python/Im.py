# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class Im(IonChannel):
    """
    
    """

    def __init__(self, name="Im"):
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

    
    def compute_kinetic_variables(self, v):
        
        qt = 2.3 ** ((34 - 21) / 10)
        mAlpha = 0.0033 * np.exp(((2.5 * 0.04) * (v - -35)))
        mBeta = 0.0033 * np.exp(((-2.5 * 0.04) * (v - -35)))
        mInf = mAlpha / (mAlpha + mBeta)
        mTau = (1 / (mAlpha + mBeta)) / qt
        return mInf, mTau
    
    