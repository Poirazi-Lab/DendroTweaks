TITLE NMDA synapse

COMMENT
Custom NMDA synapse model developed for DendroTweaks
ENDCOMMENT

NEURON {
    POINT_PROCESS NMDA
    NONSPECIFIC_CURRENT i
    RANGE gmax, mg, mgblock
    RANGE tau_rise, tau_decay
    RANGE mu, gamma
    RANGE i, g, e
}

UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (uS) = (microsiemens)
    (mM) = (millimole)
}

PARAMETER {
    gmax = 0       (uS)
    e = 0          (mV)
    tau_rise = 2   (ms)
    tau_decay = 30 (ms)
    mg = 1         (mM) 
    mu = 0.28      (/mM)
    gamma = 0.062  (/mV)
}

ASSIGNED {
    v       (mV)
    i       (nA)
    g       (uS)
    factor  (1)
    mgblock (1)
}

STATE {
    A (1)
    B (1)
}

BREAKPOINT {
    SOLVE state METHOD cnexp
    mgblock = 1 / (1 + (mu * mg) * exp(-gamma * v))
    g = mgblock * gmax * (B - A)
    i = g * (v - e)
}

DERIVATIVE state {
    A' = -A / tau_rise
    B' = -B / tau_decay
}

INITIAL {
    LOCAL tp
    A = 0
    B = 0

    tp = (tau_rise * tau_decay) / (tau_decay - tau_rise) * log(tau_decay / tau_rise)
    factor = -exp(-tp / tau_rise) + exp(-tp / tau_decay)
    factor = 1 / factor

}

NET_RECEIVE(weight (1)) {
    A = A + weight * factor
    B = B + weight * factor
}
