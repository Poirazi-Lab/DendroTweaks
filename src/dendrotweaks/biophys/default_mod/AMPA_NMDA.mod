TITLE NMDA synapse

COMMENT
Custom NMDA synapse model developed for DendroTweaks
ENDCOMMENT

NEURON {
    POINT_PROCESS AMPA_NMDA
    NONSPECIFIC_CURRENT i
    RANGE gmax_AMPA, gmax_NMDA, mg, mgblock
    RANGE tau_rise_AMPA, tau_decay_AMPA, tau_rise_NMDA, tau_decay_NMDA
    RANGE mu, gamma
    RANGE i, i_AMPA, i_NMDA, g, g_AMPA, g_NMDA, e
}

UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (uS) = (microsiemens)
    (mM) = (millimole)
}

PARAMETER {
    gmax_AMPA = 0        (uS)
    gmax_NMDA = 0        (uS)
    e = 0                (mV)
    tau_rise_AMPA = 0.1  (ms)
    tau_decay_AMPA = 2.5 (ms)
    tau_rise_NMDA = 2    (ms)
    tau_decay_NMDA = 30  (ms)
    mg = 1               (mM) 
    mu = 0.28            (/mM)
    gamma = 0.062        (/mV)
}

ASSIGNED {
    v           (mV)
    i           (nA)
    i_AMPA      (nA)
    i_NMDA      (nA)
    g           (uS)
    g_AMPA      (uS)
    g_NMDA      (uS)
    factor_AMPA (1)
    factor_NMDA (1)
    mgblock     (1)
}

STATE {
    A_AMPA (1)
    B_AMPA (1)
    A_NMDA (1)
    B_NMDA (1)
}

BREAKPOINT {
    SOLVE state METHOD cnexp
    g_AMPA = gmax_AMPA * (B_AMPA - A_AMPA)
    i_AMPA = g_AMPA * (v - e)

    mgblock = 1 / (1 + (mu * mg) * exp(-gamma * v))
    g_NMDA = mgblock * gmax_NMDA * (B_NMDA - A_NMDA)
    i_NMDA = g_NMDA * (v - e)
    
    g = g_AMPA + g_NMDA
    i = i_AMPA + i_NMDA
}

DERIVATIVE state {
    A_AMPA' = -A_AMPA / tau_rise_AMPA
    B_AMPA' = -B_AMPA / tau_decay_AMPA
    A_NMDA' = -A_NMDA / tau_rise_NMDA
    B_NMDA' = -B_NMDA / tau_decay_NMDA
}

INITIAL {
    LOCAL tp_AMPA, tp_NMDA

    A_AMPA = 0
    B_AMPA = 0

    tp_AMPA = (tau_rise_AMPA * tau_decay_AMPA) / (tau_decay_AMPA - tau_rise_AMPA) * log(tau_decay_AMPA / tau_rise_AMPA)
    factor_AMPA = -exp(-tp_AMPA / tau_rise_AMPA) + exp(-tp_AMPA / tau_decay_AMPA)
    factor_AMPA = 1 / factor_AMPA

    A_NMDA = 0
    B_NMDA = 0

    tp_NMDA = (tau_rise_NMDA * tau_decay_NMDA) / (tau_decay_NMDA - tau_rise_NMDA) * log(tau_decay_NMDA / tau_rise_NMDA)
    factor_NMDA = -exp(-tp_NMDA / tau_rise_NMDA) + exp(-tp_NMDA / tau_decay_NMDA)
    factor_NMDA = 1 / factor_NMDA

}

NET_RECEIVE(weight (1)) {
    A_AMPA = A_AMPA + weight * factor_AMPA
    B_AMPA = B_AMPA + weight * factor_AMPA
    A_NMDA = A_NMDA + weight * factor_NMDA
    B_NMDA = B_NMDA + weight * factor_NMDA
}
