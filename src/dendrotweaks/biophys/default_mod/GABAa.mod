TITLE GABAa synapse

COMMENT
Custom GABAa synapse model developed for DendroTweaks
ENDCOMMENT

NEURON {
    POINT_PROCESS GABAa
    NONSPECIFIC_CURRENT i
    RANGE gmax
    RANGE tau_rise, tau_decay
    RANGE i, g, e
}

UNITS {
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (uS) = (microsiemens)
}

PARAMETER {
    gmax = 0        (uS)
    e = -70         (mV)
    tau_rise = 0.2  (ms)
    tau_decay = 1.4 (ms)
}

ASSIGNED {
    v       (mV)
    i       (nA)
    g       (uS)
    factor  (1)
}

STATE {
    A (1)
    B (1)
}

BREAKPOINT {
    SOLVE state METHOD cnexp
    g = gmax * (B - A)
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
