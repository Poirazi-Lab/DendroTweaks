TITLE standardized {{ suffix }} channel

COMMENT
Standardized and templated by DendroTweaks.
This NMODL file defines a model for a {{ ion }} ion channel.
ENDCOMMENT

NEURON {
    SUFFIX {{ suffix }}
    {% if ion is none %}
    NONSPECIFIC_CURRENT i
    {% else %}
    USEION {{ ion }} READ e{{ ion }} WRITE i{{ ion }}
    {% endif %}
    RANGE gbar, i{% for param, _, _ in range_params %}, {{ param }}{% endfor %}
}

UNITS {
    (mA) = (milliamp)
	(mV) = (millivolt)
	(S)  = (siemens)
	(um) = (micron)
}

PARAMETER {
    {% for key, value, unit in params %}{{ "%-7s"|format(key) }} = {{ value }} ({{ unit }}){% if not loop.last %}
    {% endif %}{% endfor %}
}

ASSIGNED {
    v        (mV)     : membrane voltage
    i        (mA/cm2) : current density
    i{{ "%-7s"|format(ion) }} (mA/cm2) : current density of {{ ion }} ion
    g{{ "%-7s"|format(ion) }} (S/cm2)  : conductance of {{ ion }} ion
    e{{ "%-7s"|format(ion) }} (mV)     : reversal potential of {{ ion }} ion
    {% for state in state_vars %}
    {{ state }}_inf    (1)      : steady state value of {{ state }}
    tau_{{ state }}    (ms)     : time constant of {{ state }}
    {% endfor %}
    tadj     (1)      : temperature adjustment factor
    celsius  (degC)   : simulation temperature in celsius
}

STATE { {% for variable in state_vars %}{{ variable }}{% if not loop.last %} {% endif %}{% endfor %} }

BREAKPOINT {
    SOLVE states METHOD cnexp
    g{{ ion }} = tadj * gbar{% for state, power in state_vars.items() %} * {% if power > 1 %}pow({{ state }}, {{ power }}){% else %}{{ state }}{% endif %}{% endfor %}
    i = g{{ ion }} * (v - e{{ ion }}) 
    i{{ ion }} = i
}

DERIVATIVE states {
    rates(v)
    {% for state in state_vars %}{{ state }}' = ({{ state }}_inf - {{ state }}) / tau_{{ state }}
    {% endfor %}
}

INITIAL {
    {%- if has_tadj%}
    tadj = q10^((celsius - temp)/10(degC))
    {%- else %}
    tadj = 1
    {%- endif %}
    rates(v)
    {% for state in state_vars %}{{ state }} = {{ state }}_inf
    {% endfor %}
}


FUNCTION alpha_prime(v (mV), k (1/ms), delta (1), vhalf (mV), sigma (mV)) (1/ms) {
    alpha_prime = k * exp(delta * (v - vhalf) / sigma)
}

FUNCTION beta_prime(v (mV), k (1/ms), delta (1), vhalf (mV), sigma (mV)) (1/ms) {
    beta_prime = k * exp(-(1 - delta) * (v - vhalf) / sigma)
}                

PROCEDURE rates(v(mV)) {
    LOCAL {% for state in state_vars %}alpha_{{ state }}, beta_{{ state }}{% if not loop.last %}, {% endif %}{% endfor %}

    {% for state in state_vars %}
    {{ state }}_inf = 1 / (1 + exp(-(v - vhalf_{{ state }}) / sigma_{{ state }}))
    alpha_{{ state }} = alpha_prime(v, k_{{ state }}, delta_{{ state }}, vhalf_{{ state }}, sigma_{{ state }})
    beta_{{ state }} = beta_prime(v, k_{{ state }}, delta_{{ state }}, vhalf_{{ state }}, sigma_{{ state }})
    tau_{{ state }} = (1 / (alpha_{{ state }} + beta_{{ state }}) + tau0_{{ state }}) / tadj
    {% endfor %}
    
}


