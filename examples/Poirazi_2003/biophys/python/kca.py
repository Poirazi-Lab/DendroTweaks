# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class kca(IonChannel):
    """
    Slow Ca-dependent potassium current
    """

    def __init__(self, name="kca"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "beta": 0.03,
            "cac": 0.025,
            "taumin": 0.5
            }
        self.range_params = {
            "gbar": 0.0
            }
        self.states = {
            "m": 0.0
            }
        self._state_powers = {
            "m": {'power': 3}
            }
        self.ion = "k"
        self.current_name = "i_k"
        self.independent_var_name = "cai"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, cai):
        beta = self.params["beta"]
        cac = self.params["cac"]
        taumin = self.params["taumin"]
        
        car = (cai / cac) ** 2
        mInf = car / (1 + car)
        mTau = ((1 / beta) / (1 + car)) / self.tadj
        conditions = [mTau < taumin, ~(mTau < taumin)]
        choices = [taumin, mTau]
        mTau = np.select(conditions, choices)
        return mInf, mTau
    
    