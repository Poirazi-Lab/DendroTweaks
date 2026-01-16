# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr


from jaxley.channels import Channel
from jaxley.solver_gate import exponential_euler
import jax.numpy as np

class KCa(Channel):
    """
    Calcium-dependent potassium channel
    """

    def __init__(self, name="KCa"):
        self.current_is_in_mA_per_cm2 = True
        super().__init__(name=name)
        self.channel_params = {
            "gbar_KCa": 0.0,
            "caix_KCa": 1,
            "Ra_KCa": 0.01,
            "Rb_KCa": 0.02,
            "temp_KCa": 23,
            "q10_KCa": 2.3
            }
        self.channel_states = {
            "n_KCa": 0.0
            }
        self._state_powers = {
            "n_KCa": {'power': 1}
            }
        self.ion = "k"
        self.current_name = "i_k"

        self.independent_var_name = "cai"
        self.tadj = 1

    def set_tadj(self, temperature):
        """
        Set the temperature adjustment factor for the channel kinetics.

        Parameters
        ----------
        temperature : float
            The temperature in degrees Celsius.

        Notes
        -----
        The temperature adjustment factor is calculated as:
        tadj = q10 ** ((temperature - reference_temp) / 10)
        where q10 is the temperature coefficient and reference_temp is the
        temperature at which the channel kinetics were measured.
        """
        q10 = self.channel_params.get(f"q10_KCa")
        reference_temp = self.channel_params.get(f"temp_KCa")
        if q10 is None or reference_temp is None:
            self.tadj = 1
            print(f"Warning: q10 or reference temperature not set for {self.name}. Using default tadj = 1.")
        else:
            self.tadj = q10 ** ((temperature - reference_temp) / 10)

    def __getitem__(self, item):
        return self.channel_params[item]

    def __setitem__(self, item, value):
        self.channel_params[item] = value
        
    
    def compute_kinetic_variables(self, cai):
        caix = self.channel_params.get("caix_KCa", 1)
        Ra = self.channel_params.get("Ra_KCa", 1)
        Rb = self.channel_params.get("Rb_KCa", 1)
        
        alpn = Ra * ((1 * cai) ** caix)
        betn = Rb
        nTau = 1 / (self.tadj * (alpn + betn))
        nInf = alpn / (alpn + betn)
        return nInf, nTau

    def update_states(self, states, dt, v, params):
        n = states['n_KCa']
        cai = states["CaCon_i"]
        nInf, nTau = self.compute_kinetic_variables(cai)
        new_n = exponential_euler(n, dt, nInf, nTau)
        return {
            "n_KCa": new_n
            }

    def compute_current(self, states, v, params):
        n = states['n_KCa']
        gbar = params["gbar_KCa"]
        cai = states["CaCon_i"]
        E = params.get("E_k", -80)
        nInf, nTau = self.compute_kinetic_variables(cai)
        g = self.tadj * gbar * n**1 
        return g * (v - E)

    def init_state(self, states, v, params, delta_t):
        cai = states["CaCon_i"]
        nInf, nTau = self.compute_kinetic_variables(cai)
        return {
            "n_KCa": nInf
            }

