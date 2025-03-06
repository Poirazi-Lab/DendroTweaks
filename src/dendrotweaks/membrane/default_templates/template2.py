# This is a JINJA template file for generating Python channel class from a MOD file.

from jaxley.channels import Channel
from jaxley.solver_gate import exponential_euler
import jax.numpy as jnp

class {{ class_name }}(Channel):

    def __init__(self, name={{ class_name }}):
        super().__init__(name=name)
        prefix = self._name
        self.channel_params = {
            {% for param, value in channel_params.items() %}f"{prefix}_{{ param }}": {{ value }},{% if not loop.last %}
            {% endif %}{% endfor %}
        }
        self.channel_states = {
            {% for state in state_vars %}f"{prefix}_{{ state }}": 0.0,{% if not loop.last %}
            {% endif %}{% endfor %}
        }
        self.ion = "{{ ion }}"
        self.current_name = "i_{{ ion }}"

    {% for function in functions %}
    {{ function }}{% endfor %}

    {% for procedure in procedures %}
    {{ procedure }}{% endfor %}

    def update_states(self, states, dt, v, params):
        prefix = self._name
        self.rates(v)
        {% for state, state_params in state_vars.items() %}new_{{state}} = exponential_euler({{state}}, dt, {{state_params['inf']}}, {{state_params['tau']}}){% endfor %}
        return {
            {% for state in state_vars %}f"{prefix}_{{state}}": new_{{state}},{% endfor %}
        }

    def compute_current(self, states, v, params):
        prefix = self._name
        self.rates(v)
        g = self.tadj * params[f"{prefix}_gbar"] * {% for state, state_params in state_vars.items()%} {{state}}**{{state_params['power']}} {% endfor %} * 1000
        e_k = -80.0
        return g * (v - e_k)

