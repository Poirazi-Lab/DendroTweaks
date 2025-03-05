# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.membrane.mechanisms import IonChannel
import numpy as np

class cat(IonChannel):
    """
    t-type calcium channel with high threshold for activation
    """

    def __init__(self, name="cat"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0,
            "tBase": 23.5,
            "ki": 0.001,
            "tfa": 1,
            "tfi": 0.68
            }
        self.range_params = {
            "gbar": 0
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
        self.independent_var_name = "cai"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        tfa = self.params["tfa"]
        tfi = self.params["tfi"]
        
        a = self.alpm(v)
        mTau = 1 / (tfa * (a + self.betm(v)))
        mInf = a / (a + self.betm(v))
        a = self.alph(v)
        hTau = 1 / (tfi * (a + self.beth(v)))
        hInf = a / (a + self.beth(v))
        return mInf, mTau, hInf, hTau
    
    
    def h2(self, cai):
        ki = self.params["ki"]
        
        h2 = ki / (ki + cai)
        return h2
    
    def ghk(self, v, ci, co):
        
        f = KTF(self.temperature) / 2
        nu = v / f
        ghk = (-f * (1.0 - ((ci / co) * np.exp(nu)))) * efun(nu)
        return ghk
    
    def KTF(self, celsius):
        
        KTF = (25.0 / 293.15) * (self.temperature + 273.15)
        return KTF
    
    def efun(self, z):
        
        conditions = [np.abs(z) < 0.0001, ~(np.abs(z) < 0.0001)]
        choices = [1 - (z / 2), z / (np.exp(z) - 1)]
        efun = np.select(conditions, choices)
        return efun
    
    def alph(self, v):
        
        alph = 0.00016 * np.exp((-(v + 57) / 19))
        return alph
    
    def beth(self, v):
        
        beth = 1 / (np.exp(((-v + 15) / 10)) + 1.0)
        return beth
    
    def alpm(self, v):
        
        alpm = (0.1967 * ((-1.0 * v) + 19.88)) / (np.exp((((-1.0 * v) + 19.88) / 10.0)) - 1.0)
        return alpm
    
    def betm(self, v):
        
        betm = 0.046 * np.exp((-v / 22.73))
        return betm