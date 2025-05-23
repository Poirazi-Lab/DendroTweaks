# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

from dendrotweaks.biophys.mechanisms import IonChannel
from jaxley.channels import Channel
from jaxley.solver_gate import exponential_euler
import jax.numpy as np

class stdNa(Channel, IonChannel):
    """
    standardized stdNa channel
    """

    def __init__(self, name="stdNa"):
        self.current_is_in_mA_per_cm2 = True
        super().__init__(name=name)
        self.channel_params = {
            "vhalf_m_stdNa": -32.571,
            "sigma_m_stdNa": 9.8,
            "k_m_stdNa": 1.882,
            "delta_m_stdNa": 0.541,
            "tau0_m_stdNa": 0.065,
            "vhalf_h_stdNa": -60.0,
            "sigma_h_stdNa": -6.2,
            "k_h_stdNa": 0.018,
            "delta_h_stdNa": 0.395,
            "tau0_h_stdNa": 0.797,
            "gbar_stdNa": 0.0,
            "q10_stdNa": 2.3,
            "temp_stdNa": 23
            }
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
        self.channel_states = {
            "m_stdNa": 0.0,
            "h_stdNa": 0.0
            }
        self._state_powers = {
            "m_stdNa": {'power': 3},
            "h_stdNa": {'power': 1}
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
        vhalf_m = self.channel_params.get("vhalf_m_stdNa", 1)
        sigma_m = self.channel_params.get("sigma_m_stdNa", 1)
        k_m = self.channel_params.get("k_m_stdNa", 1)
        delta_m = self.channel_params.get("delta_m_stdNa", 1)
        tau0_m = self.channel_params.get("tau0_m_stdNa", 1)
        vhalf_h = self.channel_params.get("vhalf_h_stdNa", 1)
        sigma_h = self.channel_params.get("sigma_h_stdNa", 1)
        k_h = self.channel_params.get("k_h_stdNa", 1)
        delta_h = self.channel_params.get("delta_h_stdNa", 1)
        tau0_h = self.channel_params.get("tau0_h_stdNa", 1)
        
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
        m = states['m_stdNa']
        h = states['h_stdNa']
        mInf, mTau, hInf, hTau = self.compute_kinetic_variables(v)
        new_m = exponential_euler(m, dt, mInf, mTau)
        new_h = exponential_euler(h, dt, hInf, hTau)
        return {
            "m_stdNa": new_m,
            "h_stdNa": new_h
            }

    def compute_current(self, states, v, params):
        m = states['m_stdNa']
        h = states['h_stdNa']
        gbar = params["gbar_stdNa"]
        # E = params["E_na"]
        E = 50
        mInf, mTau, hInf, hTau = self.compute_kinetic_variables(v)
        g = self.tadj * gbar * m**3 * h**1 
        return g * (v - E)

    def init_state(self, states, v, params, delta_t):
        mInf, mTau, hInf, hTau = self.compute_kinetic_variables(v)
        return {
            "m_stdNa": mInf,
            "h_stdNa": hInf
            }

