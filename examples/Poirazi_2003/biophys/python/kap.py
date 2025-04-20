# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class kap(IonChannel):
    """
    K-A channel from Klee Ficker and Heinemann
    """

    def __init__(self, name="kap"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0,
            "vhalfn": 11,
            "vhalfl": -56,
            "a0n": 0.05,
            "zetan": -1.5,
            "zetal": 3,
            "gmn": 0.55,
            "gml": 1,
            "lmin": 2,
            "nmin": 0.1,
            "pw": -1,
            "tq": -40,
            "qq": 5,
            "q10": 5
            }
        self.range_params = {
            "gbar": 0
            }
        self.states = {
            "n": 0.0,
            "l": 0.0
            }
        self._state_powers = {
            "n": {'power': 1},
            "l": {'power': 1}
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
        a0n = self.params["a0n"]
        lmin = self.params["lmin"]
        nmin = self.params["nmin"]
        q10 = self.params["q10"]
        
        qt = q10 ** ((self.temperature - 24) / 10)
        a = self.alpn(v)
        nInf = 1 / (1 + a)
        nTau = self.betn(v) / ((qt * a0n) * (1 + a))
        conditions = [nTau < nmin, ~(nTau < nmin)]
        choices = [nmin, nTau]
        nTau = np.select(conditions, choices)
        a = self.alpl(v)
        lInf = 1 / (1 + a)
        lTau = 0.26 * (v + 50)
        conditions = [lTau < lmin, ~(lTau < lmin)]
        choices = [lmin, lTau]
        lTau = np.select(conditions, choices)
        return nInf, nTau, lInf, lTau
    
    
    def alpn(self, v):
        vhalfn = self.params["vhalfn"]
        zetan = self.params["zetan"]
        pw = self.params["pw"]
        tq = self.params["tq"]
        qq = self.params["qq"]
        
        zeta = zetan + (pw / (1 + np.exp(((v - tq) / qq))))
        alpn = np.exp(((((0.001 * zeta) * (v - vhalfn)) * 96480.0) / (8.315 * (273.16 + self.temperature))))
        return alpn
    
    def betn(self, v):
        vhalfn = self.params["vhalfn"]
        zetan = self.params["zetan"]
        gmn = self.params["gmn"]
        pw = self.params["pw"]
        tq = self.params["tq"]
        qq = self.params["qq"]
        
        zeta = zetan + (pw / (1 + np.exp(((v - tq) / qq))))
        betn = np.exp((((((0.001 * zeta) * gmn) * (v - vhalfn)) * 96480.0) / (8.315 * (273.16 + self.temperature))))
        return betn
    
    def alpl(self, v):
        vhalfl = self.params["vhalfl"]
        zetal = self.params["zetal"]
        
        alpl = np.exp(((((0.001 * zetal) * (v - vhalfl)) * 96480.0) / (8.315 * (273.16 + self.temperature))))
        return alpl
    
    def betl(self, v):
        vhalfl = self.params["vhalfl"]
        zetal = self.params["zetal"]
        gml = self.params["gml"]
        
        betl = np.exp((((((0.001 * zetal) * gml) * (v - vhalfl)) * 96480.0) / (8.315 * (273.16 + self.temperature))))
        return betl