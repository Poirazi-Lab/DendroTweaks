# This Python channel class was automatically generated from a MOD file
# using DendroTweaks toolbox, dendrotweaks.dendrites.gr

import sys

from dendrotweaks.biophys.mechanisms import IonChannel
import numpy as np

class {{ class_name }}(IonChannel):
    """
    {{ title }}
    """

    def __init__(self, name="{{ class_name }}"):
        super().__init__(name=name)
        self.params = {
            {% for param, value in channel_params.items() -%}
            "{{ param }}": {{ value }}
                {%- if not loop.last -%},
                {%- endif %}
            {% endfor -%}
        }
        self.range_params = {
            {% for param, value in range_params.items() -%}
            "{{ param }}": {{ value }}
                {%- if not loop.last -%},
                {%- endif %}
            {% endfor -%}
        }
        self.states = {
            {% for state in state_vars -%}
            "{{ state }}": 0.0
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }
        self._state_powers = {
            {% for state, power in state_vars.items() -%}
            "{{ state }}": {{ power }}
                {%- if not loop.last %},
                {%- endif %}
            {% endfor -%}
        }
        self.ion = "{{ ion }}"
        self.current_name = "i_{{ ion }}"
        self.current_available = {{ current_available }}
        self.independent_var_name = "{{ independent_var_name }}"
        self.temperature = 37

    def __getitem__(self, item):
        return self.params[item]

    def __setitem__(self, item, value):
        self.params[item] = value

    {% for procedure in procedures %}
    {{ procedure['signature'] }}
        {% for param in procedure['params'] -%}
        {{ param }} = self.params["{{ param }}"]
        {% endfor %}
        {{ procedure['body'] }}
    {%- if not loop.last %}
    {% endif %}{% endfor %}
    
    {% for function in functions %}
    {{ function['signature'] }}
        {% for param in function['params'] -%}
        {{ param }} = self.params["{{ param }}"]
        {% endfor %}
        {{ function['body'] }}
    {%- if not loop.last %}
    {% endif %}{% endfor -%}


