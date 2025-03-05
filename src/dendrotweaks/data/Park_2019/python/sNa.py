# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.membrane.mechanisms import IonChannel
import numpy as np

class sNa(IonChannel):
    """
    standardized sNa channel
    """

    def __init__(self, name="sNa"):
        super().__init__(name=name)
        self.params = {
            "vhalf_m": -32.571,
            "sigma_m": 9.8,
            "k_m": 1.882,
            "delta_m": 0.541,
            "tau0_m": 0.065,
            "vhalf_h": -60.0,
            "sigma_h": -6.2,
            "k_h": 0.018,
            "delta_h": 0.395,
            "tau0_h": 0.797,
            "gbar": 0.0,
            "q10": 2.3,
            "temp": 23
            }
        self.range_params = {
            "vhalf_m": -32.571,
            "sigma_m": 9.8,
            "k_m": 1.882,
            "delta_m": 0.541,
            "tau0_m": 0.065,
            "vhalf_h": -60.0,
            "sigma_h": -6.2,
            "k_h": 0.018,
            "delta_h": 0.395,
            "tau0_h": 0.797,
            "gbar": 0.0,
            "q10": 2.3,
            "temp": 23
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
        vhalf_m = self.params["vhalf_m"]
        sigma_m = self.params["sigma_m"]
        k_m = self.params["k_m"]
        delta_m = self.params["delta_m"]
        tau0_m = self.params["tau0_m"]
        vhalf_h = self.params["vhalf_h"]
        sigma_h = self.params["sigma_h"]
        k_h = self.params["k_h"]
        delta_h = self.params["delta_h"]
        tau0_h = self.params["tau0_h"]
        
        mInf = 1 / (1 + np.exp((-(v - vhalf_m) / sigma_m)))
        alpha_m = self.alpha_prime(v, k_m, delta_m, vhalf_m, sigma_m)
        beta_m = self.beta_prime(v, k_m, delta_m, vhalf_m, sigma_m)
        mTau = ((1 / (alpha_m + beta_m)) + tau0_m) / self.tadj
        hInf = 1 / (1 + np.exp((-(v - vhalf_h) / sigma_h)))
        alpha_h = self.alpha_prime(v, k_h, delta_h, vhalf_h, sigma_h)
        beta_h = self.beta_prime(v, k_h, delta_h, vhalf_h, sigma_h)
        hTau = ((1 / (alpha_h + beta_h)) + tau0_h) / self.tadj
        return mInf, mTau, hInf, hTau
    
    
    def alpha_prime(self, v, k, delta, vhalf, sigma):
        
        alpha_prime = k * np.exp(((delta * (v - vhalf)) / sigma))
        return alpha_prime
    
    def beta_prime(self, v, k, delta, vhalf, sigma):
        
        beta_prime = k * np.exp(((-(1 - delta) * (v - vhalf)) / sigma))
        return beta_prime