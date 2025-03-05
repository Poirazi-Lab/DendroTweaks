# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from chanopy.mechanisms import IonChannel
import numpy as np

class {{ class_name }}(IonChannel):
    """
    {{ title }}
    """

    def __init__(self, name="{{ class_name }}"):
        super().__init__(name=name)
        self.channel_params = {
            {% for param, value in channel_params.items() -%}
            "{{ param }}_{{ class_name }}": {{ value }}
                {%- if not loop.last -%},
                {%- endif %}
            {% endfor -%},
            "celsius": 37
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

    def __getitem__(self, item):
        return self.channel_params[item]

    def __setitem__(self, item, value):
        self.channel_params[item] = value

    @property
    def params(self):
        return self.channel_params

    {% for procedure in procedures %}
    {{ procedure['signature'] }}
        {% for param in procedure['params'] -%}
        {{ param }} = self.params["{{ param }}_{{ class_name }}"]
        {% endfor %}
        celsius = self.params["celsius"]
        {{ procedure['body'] }}
    {%- if not loop.last %}
    {% endif %}{% endfor %}

    def tadj(self, **params):
        """
        Calculate the temperature adjustment factor.
        """
        q10 = params.get("{{ class_name }}_q10", 1)
        celsius = params.get("celsius", 37)
        temp = params.get("{{ class_name }}_temp", 23)
        return q10 ** ((celsius - temp) / 10)
    
    {% for function in functions %}
    {{ function['signature'] }}
        {% for param in function['params'] -%}
        {{ param }} = self.params["{{ param }}_{{ class_name }}"]
        {% endfor %}
        {{ function['body'] }}
    {%- if not loop.last %}
    {% endif %}{% endfor -%}


