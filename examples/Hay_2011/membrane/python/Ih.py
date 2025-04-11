# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class Ih(IonChannel):
    """
    
    """

    def __init__(self, name="Ih"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "ehcn": -45.0
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
        self.ion = "None"
        self.current_name = "i_None"
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self):
        
        conditions = [v == -154.9, ~(v == -154.9)]
        choices = [v + 0.0001, v]
        v = np.select(conditions, choices)
        mAlpha = ((0.001 * 6.43) * (v + 154.9)) / (np.exp(((v + 154.9) / 11.9)) - 1)
        mBeta = (0.001 * 193) * np.exp((v / 33.1))
        mInf = mAlpha / (mAlpha + mBeta)
        mTau = 1 / (mAlpha + mBeta)
        return mInf, mTau
    
    