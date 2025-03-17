# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.membrane.mechanisms import IonChannel
import numpy as np

class K_Pst(IonChannel):
    """
    
    """

    def __init__(self, name="K_Pst"):
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
        self.ion = "k"
        self.current_name = "i_k"
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self):
        
        qt = 2.3 ** ((34 - 21) / 10)
        v = v + 10
        mInf = 1 / (1 + np.exp((-(v + 1) / 12)))
        conditions = [v < -50, ~(v < -50)]
        choices = [(1.25 + (175.03 * np.exp((-v * -0.026)))) / qt, (1.25 + (13 * np.exp((-v * 0.026)))) / qt]
        mTau = np.select(conditions, choices)
        hInf = 1 / (1 + np.exp((-(v + 54) / -11)))
        hTau = (360 + ((1010 + (24 * (v + 55))) * np.exp((-((v + 75) / 48) ** 2)))) / qt
        v = v - 10
        return mInf, mTau, hInf, hTau
    
    