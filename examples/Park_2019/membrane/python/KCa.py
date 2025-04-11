# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class KCa(IonChannel):
    """
    Calcium-dependent potassium channel
    """

    def __init__(self, name="KCa"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "caix": 1,
            "Ra": 0.01,
            "Rb": 0.02,
            "temp": 23,
            "q10": 2.3
            }
        self.range_params = {
            "gbar": 0.0
            }
        self.states = {
            "n": 0.0
            }
        self._state_powers = {
            "n": {'power': 1}
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
        caix = self.params["caix"]
        Ra = self.params["Ra"]
        Rb = self.params["Rb"]
        
        alpn = Ra * ((1 * cai) ** caix)
        betn = Rb
        nTau = 1 / (self.tadj * (alpn + betn))
        nInf = alpn / (alpn + betn)
        return nInf, nTau
    
    