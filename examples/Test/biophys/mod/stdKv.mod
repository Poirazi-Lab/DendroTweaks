TITLE standardized stdKv channel

COMMENT
Standardized and templated by DendroTweaks.
This NMODL file defines a model for a k ion channel.
ENDCOMMENT

NEURON {
    SUFFIX stdKv
    
    USEION k READ ek WRITE ik
    
    RANGE gbar, i, vhalf_n, sigma_n, k_n, delta_n, tau0_n, gbar, q10, temp
}

UNITS {
    (mA) = (milliamp)
	(mV) = (millivolt)
	(S)  = (siemens)
	(um) = (micron)
}

PARAMETER {
    vhalf_n = 14.164 (mV)
    sigma_n = 9.0 (mV)
    k_n     = 0.123 (1/ms)
    delta_n = 0.732 (1)
    tau0_n  = 0.877 (ms)
    gbar    = 0.0 (S/cm2)
    q10     = 2.3 (1)
    temp    = 23 (degC)
}

ASSIGNED {
    v        (mV)     : membrane voltage
    i        (mA/cm2) : current density
    ik       (mA/cm2) : current density of k ion
    gk       (S/cm2)  : conductance of k ion
    ek       (mV)     : reversal potential of k ion
    
    n_inf    (1)      : steady state value of n
    tau_n    (ms)     : time constant of n
    
    tadj     (1)      : temperature adjustment factor
    celsius  (degC)   : simulation temperature in celsius
}

STATE { n }

BREAKPOINT {
    SOLVE states METHOD cnexp
    gk = tadj * gbar * n
    i = gk * (v - ek) 
    ik = i
}

DERIVATIVE states {
    rates(v)
    n' = (n_inf - n) / tau_n
    
}

INITIAL {
    tadj = q10^((celsius - temp)/10(degC))
    rates(v)
    n = n_inf
    
}


FUNCTION alpha_prime(v (mV), k (1/ms), delta (1), vhalf (mV), sigma (mV)) (1/ms) {
    alpha_prime = k * exp(delta * (v - vhalf) / sigma)
}

FUNCTION beta_prime(v (mV), k (1/ms), delta (1), vhalf (mV), sigma (mV)) (1/ms) {
    beta_prime = k * exp(-(1 - delta) * (v - vhalf) / sigma)
}                

PROCEDURE rates(v(mV)) {
    LOCAL alpha_n, beta_n

    
    n_inf = 1 / (1 + exp(-(v - vhalf_n) / sigma_n))
    alpha_n = alpha_prime(v, k_n, delta_n, vhalf_n, sigma_n)
    beta_n = beta_prime(v, k_n, delta_n, vhalf_n, sigma_n)
    tau_n = (1 / (alpha_n + beta_n) + tau0_n) / tadj
    
    
}

