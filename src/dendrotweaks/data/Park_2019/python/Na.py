# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.membrane.mechanisms import IonChannel
import numpy as np

class Na(IonChannel):
    """
    Na channel
    """

    def __init__(self, name="Na"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "Rma": 0.182,
            "Rmb": 0.14,
            "v12m": -30,
            "qm": 9.8,
            "Rhb": 0.0091,
            "Rha": 0.024,
            "v12ha": -45,
            "v12hb": -70,
            "qh": 5,
            "v12hinf": -60,
            "qhinf": 6.2,
            "temp": 23,
            "q10": 2.3
            }
        self.range_params = {
            "gbar": 0.0,
            "Rma": 0.182,
            "Rmb": 0.14,
            "v12m": -30,
            "qm": 9.8,
            "Rhb": 0.0091,
            "Rha": 0.024,
            "v12ha": -45,
            "v12hb": -70,
            "qh": 5,
            "v12hinf": -60,
            "qhinf": 6.2
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

    
    def compute_kinetic_variables(self, v):
        Rma = self.params["Rma"]
        Rmb = self.params["Rmb"]
        v12m = self.params["v12m"]
        qm = self.params["qm"]
        Rhb = self.params["Rhb"]
        Rha = self.params["Rha"]
        v12ha = self.params["v12ha"]
        v12hb = self.params["v12hb"]
        qh = self.params["qh"]
        v12hinf = self.params["v12hinf"]
        qhinf = self.params["qhinf"]
        
        alpm = self.rateconst(v, Rma, v12m, qm)
        betm = self.rateconst(-v, Rmb, -v12m, qm)
        alph = self.rateconst(v, Rha, v12ha, qh)
        beth = self.rateconst(-v, Rhb, -v12hb, qh)
        mTau = 1 / (self.tadj * (alpm + betm))
        mInf = alpm / (alpm + betm)
        hTau = 1 / (self.tadj * (alph + beth))
        hInf = 1 / (1 + np.exp(((v - v12hinf) / qhinf)))
        return mInf, mTau, hInf, hTau
    
    
    def rateconst2(self, v, r, v12, q):
        
        conditions = [np.abs(((v - v12) / q)) > 1e-06, ~(np.abs(((v - v12) / q)) > 1e-06)]
        choices = [(r * (v - v12)) / (1 - np.exp((-(v - v12) / q))), r * q]
        rateconst2 = np.select(conditions, choices)
        return rateconst2
    
    def rateconst(self, v, r, v12, q):
        
        conditions = [np.abs(((v - v12) / q)) > 1e-06, ~(np.abs(((v - v12) / q)) > 1e-06)]
        choices = [(r * (v - v12)) / (1 - np.exp((-(v - v12) / q))), r * q]
        rateconst = np.select(conditions, choices)
        return rateconst