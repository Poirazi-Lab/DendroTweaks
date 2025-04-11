# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class CaHVA(IonChannel):
    """
    HVA Ca current
    """

    def __init__(self, name="CaHVA"):
        super().__init__(name=name)
        self.params = {
            "gbar": 0.0,
            "Rma": 0.5,
            "Rmb": 0.1,
            "v12ma": -27,
            "v12mb": -75,
            "qma": 3.8,
            "qmb": 17,
            "Rha": 0.000457,
            "Rhb": 0.0065,
            "v12ha": -13,
            "v12hb": -15,
            "qha": 50,
            "qhb": 28,
            "temp": 23,
            "q10": 2.3
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
        self.independent_var_name = "v"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    
    def compute_kinetic_variables(self, vm):
        Rma = self.params["Rma"]
        Rmb = self.params["Rmb"]
        v12ma = self.params["v12ma"]
        v12mb = self.params["v12mb"]
        qma = self.params["qma"]
        qmb = self.params["qmb"]
        Rha = self.params["Rha"]
        Rhb = self.params["Rhb"]
        v12ha = self.params["v12ha"]
        v12hb = self.params["v12hb"]
        qha = self.params["qha"]
        qhb = self.params["qhb"]
        
        alpm = self.f_lexp(vm, Rma, v12ma, qma)
        betm = self.f_exp(vm, Rmb, v12mb, qmb)
        mTau = 1 / (self.tadj * (alpm + betm))
        mInf = alpm / (alpm + betm)
        alph = self.f_exp(vm, Rha, v12ha, qha)
        beth = self.f_sigm(vm, Rhb, v12hb, qhb)
        hTau = 1 / (self.tadj * (alph + beth))
        hInf = alph / (alph + beth)
        return mInf, mTau, hInf, hTau
    
    
    def f_lexp(self, v, R, v12, q):
        
        dv = -(v - v12)
        f_lexp = (R * dv) / (np.exp((dv / q)) - 1)
        return f_lexp
    
    def f_exp(self, v, R, v12, q):
        
        dv = -(v - v12)
        f_exp = R * np.exp((dv / q))
        return f_exp
    
    def f_sigm(self, v, R, v12, q):
        
        dv = -(v - v12)
        f_sigm = R / (1 + np.exp((dv / q)))
        return f_sigm