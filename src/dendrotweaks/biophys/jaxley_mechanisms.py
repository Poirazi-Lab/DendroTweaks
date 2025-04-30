from jaxley.channels import Channel
from jaxley.solver_gate import exponential_euler
import jax.numpy as jnp

class JaxleyLeakChannel(Channel):
    """Leakage current"""

    def __init__(self, name = 'Leak'):
        self.current_is_in_mA_per_cm2=True
        super().__init__(name)
        prefix = self._name
        self.channel_params = {
            f"gbar_{prefix}": 0,  # S/cm^2
            f"e_{prefix}": -70.0,  # mV
        }
        self.channel_states = {}
        self.current_name = f"i_Leak"

    def update_states(
        self, states, dt, v, params
    ):
        """No state to update."""
        return {}

    def compute_current(
        self, states, v, params
    ):
        """Return current."""
        # Multiply with 1000 to convert Siemens to milli Siemens.
        prefix = self._name
        leak_conds = params[f"gbar_{prefix}"]  # S/cm^2
        return leak_conds * (v - params[f"e_{prefix}"])

    def init_state(self, states, v, params, delta_t):
        """Initialize the state such at fixed point of gate dynamics."""
        return {}

    @property
    def range_params(self):
        return {
            param.replace(f"_{self._name}", ""): value
            for param, value in self.channel_params.items()            
        }

    @property
    def range_params_with_suffix(self):
        """
        The range parameters of the mechanism with the suffix
        — the name of the mechanism. The range parameters are the parameters
        defined in the RANGE block of the NMODL file.

        Returns
        -------
        dict
            A dictionary of the range parameters of the mechanism with the suffix and their values.
        """
        return self.channel_params



