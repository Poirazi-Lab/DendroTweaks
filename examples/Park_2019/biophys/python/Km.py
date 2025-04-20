# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class Km(IonChannel):
    """
    V-g K+ channel (Muscarinic or M-Type?)
    """

    def __init__(self, name="Km"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "Ra": 0.001,
            "Rb": 0.001,
            "v12": -30,
            "q": 9,
            "temp": 23,
            "q10": 2.3
            }
        self.range_params = {
            "gbar": 0.0,
            "v12": -30,
            "q": 9
            }
        self.states = {
            "n": 0.0
            }
        self._state_powers = {
            "n": {'power': 1}
            }
        self.ion = "k"
        self.current_name = "i_k"
        self.current_available = True
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        Ra = self.params["Ra"]
        Rb = self.params["Rb"]
        v12 = self.params["v12"]
        q = self.params["q"]
        
        alpn = self.rateconst(v, Ra, v12, q)
        betn = self.rateconst(v, -Rb, v12, -q)
        nTau = (1 / self.tadj) / (alpn + betn)
        nInf = alpn / (alpn + betn)
        return nInf, nTau
    
    
    def rateconst(self, v, r, th, q):
        
        rateconst = (r * (v - th)) / (1 - np.exp((-(v - th) / q)))
        return rateconst