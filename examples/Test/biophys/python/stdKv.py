# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

from dendrotweaks.biophys.mechanisms import IonChannel
from jaxley.channels import Channel
from jaxley.solver_gate import exponential_euler
import jax.numpy as np

class stdKv(Channel, IonChannel):
    """
    standardized stdKv channel
    """

    def __init__(self, name="stdKv"):
        self.current_is_in_mA_per_cm2 = True
        super().__init__(name=name)
        self.channel_params = {
            "vhalf_n_stdKv": 14.164,
            "sigma_n_stdKv": 9.0,
            "k_n_stdKv": 0.123,
            "delta_n_stdKv": 0.732,
            "tau0_n_stdKv": 0.877,
            "gbar_stdKv": 0.0,
            "q10_stdKv": 2.3,
            "temp_stdKv": 23
            }
        self.params = {
            "vhalf_n": 14.164,
            "sigma_n": 9.0,
            "k_n": 0.123,
            "delta_n": 0.732,
            "tau0_n": 0.877,
            "gbar": 0.0,
            "q10": 2.3,
            "temp": 23
            }
        self.range_params = {
            "vhalf_n": 14.164,
            "sigma_n": 9.0,
            "k_n": 0.123,
            "delta_n": 0.732,
            "tau0_n": 0.877,
            "gbar": 0.0,
            "q10": 2.3,
            "temp": 23
            }
        self.channel_states = {
            "n_stdKv": 0.0
            }
        self._state_powers = {
            "n_stdKv": {'power': 1}
            }
        self.ion = "k"
        self.current_name = "i_k"

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
        vhalf_n = self.channel_params.get("vhalf_n_stdKv", 1)
        sigma_n = self.channel_params.get("sigma_n_stdKv", 1)
        k_n = self.channel_params.get("k_n_stdKv", 1)
        delta_n = self.channel_params.get("delta_n_stdKv", 1)
        tau0_n = self.channel_params.get("tau0_n_stdKv", 1)
        
        nInf = 1 / (1 + np.exp((-(v - vhalf_n) / sigma_n)))
        alpha_n = self.alpha_prime(v, k_n, delta_n, vhalf_n, sigma_n)
        beta_n = self.beta_prime(v, k_n, delta_n, vhalf_n, sigma_n)
        nTau = ((1 / (alpha_n + beta_n)) + tau0_n) / self.tadj
        return nInf, nTau

    def update_states(self, states, dt, v, params):
        n = states['n_stdKv']
        nInf, nTau = self.compute_kinetic_variables(v)
        new_n = exponential_euler(n, dt, nInf, nTau)
        return {
            "n_stdKv": new_n
            }

    def compute_current(self, states, v, params):
        n = states['n_stdKv']
        gbar = params["gbar_stdKv"]
        # E = params["E_k"]
        E = -77
        nInf, nTau = self.compute_kinetic_variables(v)
        g = self.tadj * gbar * n**1 
        return g * (v - E)

    def init_state(self, states, v, params, delta_t):
        nInf, nTau = self.compute_kinetic_variables(v)
        return {
            "n_stdKv": nInf
            }

