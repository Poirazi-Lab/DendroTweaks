# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

from jaxley.channels import Channel
from jaxley.solver_gate import exponential_euler
import jax.numpy as jn 

class stdNa(Channel):
    """
    standardized stdNa channel
    """

    def __init__(self, name="stdNa"):
        super().__init__(name=name)
        self.channel_params = {
            "stdNa_vhalf_m": -32.571,
            "stdNa_sigma_m": 9.8,
            "stdNa_k_m": 1.882,
            "stdNa_delta_m": 0.541,
            "stdNa_tau0_m": 0.065,
            "stdNa_vhalf_h": -60.0,
            "stdNa_sigma_h": -6.2,
            "stdNa_k_h": 0.018,
            "stdNa_delta_h": 0.395,
            "stdNa_tau0_h": 0.797,
            "stdNa_gbar": 0.0,
            "stdNa_q10": 2.3,
            "stdNa_temp": 23
            }
        self.channel_states = {
            "stdNa_m": 0.0,
            "stdNa_h": 0.0
            }
        self._state_powers = {
            "stdNa_m": {'power': 3},
            "stdNa_h": {'power': 1}
            }
        self.ion = "na"
        self.current_name = "i_na"

        self.independent_var_name = "v"

    # @property
    # def tadj(self):
    #     return self.tadj = q10 ** ((celsius - temp) / 10)

    def __getitem__(self, item):
        return self.channel_params[item]

    def __setitem__(self, item, value):
        self.channel_params[item] = value
        
    
    def alpha_prime(self, v, k, delta, vhalf, sigma):
        alpha_prime = k * np.exp(((delta * (v - vhalf)) / sigma))
        return alpha_prime
    
    
    def beta_prime(self, v, k, delta, vhalf, sigma):
        beta_prime = k * np.exp(((-(1 - delta) * (v - vhalf)) / sigma))
        return beta_prime
    
    def compute_kinetic_variables(self, v):
        vhalf_m = self.channel_params.get("stdNa_vhalf_m", 1)
        sigma_m = self.channel_params.get("stdNa_sigma_m", 1)
        k_m = self.channel_params.get("stdNa_k_m", 1)
        delta_m = self.channel_params.get("stdNa_delta_m", 1)
        tau0_m = self.channel_params.get("stdNa_tau0_m", 1)
        vhalf_h = self.channel_params.get("stdNa_vhalf_h", 1)
        sigma_h = self.channel_params.get("stdNa_sigma_h", 1)
        k_h = self.channel_params.get("stdNa_k_h", 1)
        delta_h = self.channel_params.get("stdNa_delta_h", 1)
        tau0_h = self.channel_params.get("stdNa_tau0_h", 1)
        
        mInf = 1 / (1 + np.exp((-(v - vhalf_m) / sigma_m)))
        alpha_m = self.alpha_prime(v, k_m, delta_m, vhalf_m, sigma_m)
        beta_m = self.beta_prime(v, k_m, delta_m, vhalf_m, sigma_m)
        mTau = ((1 / (alpha_m + beta_m)) + tau0_m) / self.tadj
        hInf = 1 / (1 + np.exp((-(v - vhalf_h) / sigma_h)))
        alpha_h = self.alpha_prime(v, k_h, delta_h, vhalf_h, sigma_h)
        beta_h = self.beta_prime(v, k_h, delta_h, vhalf_h, sigma_h)
        hTau = ((1 / (alpha_h + beta_h)) + tau0_h) / self.tadj
        return mInf, mTau, hInf, hTau

    def update_states(self, states, dt, v, params):
        m = states['stdNa_m']
        h = states['stdNa_h']
        mInf, mTau, hInf, hTau = self.compute_kinetic_variables(v)
        new_m = exponential_euler(m, dt, mInf, mTau)
        new_h = exponential_euler(h, dt, hInf, hTau)
        return {
            "stdNa_m": new_m,
            "stdNa_h": new_h
            }

    def compute_current(self, states, v, params):
        m = states['stdNa_m']
        h = states['stdNa_h']
        gbar = params["stdNa_gbar"]
        # E = params["E_na"]
        E = 60
        mInf, mTau, hInf, hTau = self.compute_kinetic_variables(v)
        g = self.tadj * gbar * m**{'power': 3} * h**{'power': 1} * 1000
        return g * (v - E)

    def init_state(self, states, v, params, delta_t):
        mInf, mTau, hInf, hTau = self.compute_kinetic_variables(v)
        return {
            "stdNa_m": mInf,
            "stdNa_h": hInf
            }

