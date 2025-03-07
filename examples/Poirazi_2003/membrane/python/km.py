# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.membrane.mechanisms import IonChannel
import numpy as np

class km(IonChannel):
    """
    Km channel
    """

    def __init__(self, name="km"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0,
            "tha": -30,
            "qa": 9,
            "Ra": 0.001,
            "Rb": 0.001,
            "temp": 23,
            "q10": 2.3
            }
        self.range_params = {
            "gbar": 0
            }
        self.states = {
            "n": 0.0
            }
        self._state_powers = {
            "n": {'power': 1}
            }
        self.ion = "k"
        self.current_name = "i_k"
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        tha = self.params["tha"]
        qa = self.params["qa"]
        Ra = self.params["Ra"]
        Rb = self.params["Rb"]
        
        a = (Ra * (v - tha)) / (1 - np.exp((-(v - tha) / qa)))
        b = (-Rb * (v - tha)) / (1 - np.exp(((v - tha) / qa)))
        nTau = 1 / (a + b)
        nInf = a * nTau
        return nInf, nTau
    
    