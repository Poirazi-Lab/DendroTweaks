# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

from jaxley.channels import Channel
from jaxley.solver_gate import exponential_euler
import jax.numpy as jn 

class {{ class_name }}(Channel):
    """
    {{ title }}
    """

    def __init__(self, name="{{ class_name }}"):
        super().__init__(name=name)
        self.channel_params = {
            {% for param, value in channel_params.items() -%}
            "{{ class_name }}_{{ param }}": {{ value }}
                {%- if not loop.last -%},
                {%- endif %}
            {% endfor -%}
        }
        self.channel_states = {
            {% for state in state_vars -%}
            "{{class_name}}_{{ state }}": 0.0
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }
        self._state_powers = {
            {% for state, power in state_vars.items() -%}
            "{{class_name}}_{{ state }}": {{ power }}
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }
        self.ion = "{{ ion }}"
        self.current_name = "i_{{ ion }}"

        self.independent_var_name = "{{ independent_var_name }}"

    # @property
    # def tadj(self):
    #     return self.tadj = q10 ** ((celsius - temp) / 10)

    def __getitem__(self, item):
        return self.channel_params[item]

    def __setitem__(self, item, value):
        self.channel_params[item] = value
        
    {% for function in functions %}
    {{ function['signature'] }}
        {%- for param in function['params'] -%}
        {{ param }} = self.channel_params.get("{{ class_name }}_{{ param }}", 1)
        {% endfor %}
        {{ function['body'] }}
    {% if not loop.last %}
    {% endif %}{% endfor -%}
    {% for procedure in procedures %}
    {{ procedure['signature'] }}
        {% for param in procedure['params'] -%}
        {{ param }} = self.channel_params.get("{{ class_name }}_{{ param }}", 1)
        {% endfor %}
        {{ procedure['body'] }}
    {%- if not loop.last %}
    {% endif %}{% endfor %}

    def update_states(self, states, dt, v, params):
        {% for state, state_params in state_vars.items() -%}
        {{state}} = states['{{class_name}}_{{state}}']
            {%- if not loop.last %}
            {%- endif %}
        {% endfor -%}
        {{- procedure_calls}}
        {% for state in state_vars.keys() %}new_{{state}} = exponential_euler({{state}}, dt, {{state}}Inf, {{state}}Tau){% if not loop.last %}
        {% endif %}{% endfor %}
        return {
            {% for state in state_vars -%}
            "{{class_name}}_{{state}}": new_{{state}}
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }

    def compute_current(self, states, v, params):
        {% for state in state_vars.keys() -%}
        {{state}} = states['{{class_name}}_{{state}}']
            {%- if not loop.last %}
            {%- endif %}
        {% endfor -%}
        gbar = params["{{class_name}}_gbar"]
        # E = params["E_{{ ion }}"]
        E = {{ E_ion }}
        {{ procedure_calls}}
        g = self.tadj * gbar *{% for state, power in state_vars.items()%} {{state}}**{{power}} {% if not loop.last %}*{% endif %}{% endfor %}* 1000
        return g * (v - E)

    def init_state(self, states, v, params, delta_t):
        {{ procedure_calls}}
        return {
            {% for state in state_vars.keys() -%}
            "{{class_name}}_{{state}}": {{state}}Inf 
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }


