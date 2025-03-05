# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.membrane.mechanisms import IonChannel
import numpy as np

class mykca(IonChannel):
    """
    CaGk
    """

    def __init__(self, name="mykca"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "d1": 0.84,
            "d2": 1.0,
            "k1": 0.18,
            "k2": 0.011,
            "bbar": 0.28,
            "abar": 0.48
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
        self.independent_var_name = "cai"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v, ca):
        
        a = self.alp(v, ca)
        b = self.bet(v, ca)
        mTau = 1 / (a + b)
        mInf = a * mTau
        return mInf, mTau
    
    
    def alp(self, v, ca):
        d1 = self.params["d1"]
        k1 = self.params["k1"]
        abar = self.params["abar"]
        
        alp = abar / (1 + (exp1(k1, d1, v) / ca))
        return alp
    
    def bet(self, v, ca):
        d2 = self.params["d2"]
        k2 = self.params["k2"]
        bbar = self.params["bbar"]
        
        bet = bbar / (1 + (ca / exp1(k2, d2, v)))
        return bet
    
    def exp1(self, k, d, v):
        
        exp1 = k * np.exp(((((((-2 * d) * FARADAY) * 0.001) * v) / R) / (273.15 + self.temperature)))
        return exp1