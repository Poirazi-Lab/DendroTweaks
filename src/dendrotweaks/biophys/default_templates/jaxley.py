# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr


from jaxley.channels import Channel
from jaxley.solver_gate import exponential_euler
import jax.numpy as np

class {{ class_name }}(Channel):
    """
    {{ title }}
    """

    def __init__(self, name="{{ class_name }}"):
        self.current_is_in_mA_per_cm2 = True
        super().__init__(name=name)
        self.channel_params = {
            {% for param, value in channel_params.items() -%}
            "{{ param }}_{{ class_name }}": {{ value }}
                {%- if not loop.last -%},
                {%- endif %}
            {% endfor -%}
        }
        self.channel_states = {
            {% for state in state_vars -%}
            "{{ state }}_{{class_name}}": 0.0
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }
        self._state_powers = {
            {% for state, power in state_vars.items() -%}
            "{{ state }}_{{class_name}}": {{ power }}
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }
        self.ion = "{{ ion }}"
        self.current_name = "i_{{ ion }}"

        self.independent_var_name = "{{ independent_var_name }}"
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
        q10 = self.channel_params.get(f"q10_{{ class_name }}")
        reference_temp = self.channel_params.get(f"temp_{{ class_name }}")
        if q10 is None or reference_temp is None:
            self.tadj = 1
            print(f"Warning: q10 or reference temperature not set for {self.name}. Using default tadj = 1.")
        else:
            self.tadj = q10 ** ((temperature - reference_temp) / 10)

    def __getitem__(self, item):
        return self.channel_params[item]

    def __setitem__(self, item, value):
        self.channel_params[item] = value
        
    {% for function in functions %}
    {{ function['signature'] }}
        {%- for param in function['params'] -%}
        {{ param }} = self.channel_params.get("{{ param }}_{{ class_name }}", 1)
        {% endfor %}
        {{ function['body'] }}
    {% if not loop.last %}
    {% endif %}{% endfor -%}
    {% for procedure in procedures %}
    {{ procedure['signature'] }}
        {% for param in procedure['params'] -%}
        {{ param }} = self.channel_params.get("{{ param }}_{{ class_name }}", 1)
        {% endfor %}
        {{ procedure['body'] }}
    {%- if not loop.last %}
    {% endif %}{% endfor %}

    def update_states(self, states, dt, v, params):
        {% for state, state_params in state_vars.items() -%}
        {{state}} = states['{{ state }}_{{class_name}}']
            {%- if not loop.last %}
            {%- endif %}
        {% endfor -%}
        {{- procedure_calls}}
        {% for state in state_vars.keys() %}new_{{state}} = exponential_euler({{state}}, dt, {{state}}Inf, {{state}}Tau){% if not loop.last %}
        {% endif %}{% endfor %}
        return {
            {% for state in state_vars -%}
            "{{ state }}_{{class_name}}": new_{{state}}
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }

    def compute_current(self, states, v, params):
        {% for state in state_vars.keys() -%}
        {{state}} = states['{{ state }}_{{class_name}}']
            {%- if not loop.last %}
            {%- endif %}
        {% endfor -%}
        gbar = params["gbar_{{class_name}}"]
        # E = params["E_{{ ion }}"]
        E = {{ E_ion }}
        {{ procedure_calls}}
        g = self.tadj * gbar *{% for state, power in state_vars.items()%} {{state}}**{{power['power']}} {% if not loop.last %}*{% endif %}{% endfor %}
        return g * (v - E)

    def init_state(self, states, v, params, delta_t):
        {{ procedure_calls}}
        return {
            {% for state in state_vars.keys() -%}
            "{{ state }}_{{class_name}}": {{state}}Inf 
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }


