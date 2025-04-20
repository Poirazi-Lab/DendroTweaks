# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class CaLVA(IonChannel):
    """
    T-type Ca channel
    """

    def __init__(self, name="CaLVA"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "v12m": 50,
            "v12h": 78,
            "vwm": 7.4,
            "vwh": 5.0,
            "am": 3,
            "ah": 85,
            "vm1": 25,
            "vm2": 100,
            "vh1": 46,
            "vh2": 405,
            "wm1": 20,
            "wm2": 15,
            "wh1": 4,
            "wh2": 50
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
        self.ion = "ca"
        self.current_name = "i_ca"
        self.current_available = False
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, v):
        v12m = self.params["v12m"]
        v12h = self.params["v12h"]
        vwm = self.params["vwm"]
        vwh = self.params["vwh"]
        am = self.params["am"]
        ah = self.params["ah"]
        vm1 = self.params["vm1"]
        vm2 = self.params["vm2"]
        vh1 = self.params["vh1"]
        vh2 = self.params["vh2"]
        wm1 = self.params["wm1"]
        wm2 = self.params["wm2"]
        wh1 = self.params["wh1"]
        wh2 = self.params["wh2"]
        
        mInf = 1.0 / (1 + np.exp((-(v + v12m) / vwm)))
        hInf = 1.0 / (1 + np.exp(((v + v12h) / vwh)))
        mTau = am + (1.0 / (np.exp(((v + vm1) / wm1)) + np.exp((-(v + vm2) / wm2))))
        hTau = ah + (1.0 / (np.exp(((v + vh1) / wh1)) + np.exp((-(v + vh2) / wh2))))
        return mInf, mTau, hInf, hTau
    
    