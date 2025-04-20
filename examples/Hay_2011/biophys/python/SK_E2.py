# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class SK_E2(IonChannel):
    """
    
    """

    def __init__(self, name="SK_E2"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "zTau": 1
            }
        self.range_params = {
            "gbar": 0.0
            }
        self.states = {
            "z": 0.0
            }
        self._state_powers = {
            "z": {'power': 1}
            }
        self.ion = "k"
        self.current_name = "i_k"
        self.current_available = False
        self.independent_var_name = "cai"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, cai):
        zTau = self.params["zTau"]
        
        conditions = [cai < 1e-07, ~(cai < 1e-07)]
        choices = [cai + 1e-07, cai]
        cai = np.select(conditions, choices)
        zInf = 1 / (1 + ((0.00043 / cai) ** 4.8))
        return zInf, zTau
    
    