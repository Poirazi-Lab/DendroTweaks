TITLE standardized stdNa channel

COMMENT
Standardized and templated by DendroTweaks.
This NMODL file defines a model for a na ion channel.
ENDCOMMENT

NEURON {
    SUFFIX stdNa
    
    USEION na READ ena WRITE ina
    
    RANGE gbar, i, vhalf_m, sigma_m, k_m, delta_m, tau0_m, vhalf_h, sigma_h, k_h, delta_h, tau0_h, gbar, q10, temp
}

UNITS {
    (mA) = (milliamp)
	(mV) = (millivolt)
	(S)  = (siemens)
	(um) = (micron)
}

PARAMETER {
    vhalf_m = -32.571 (mV)
    sigma_m = 9.8 (mV)
    k_m     = 1.882 (1/ms)
    delta_m = 0.541 (1)
    tau0_m  = 0.065 (ms)
    vhalf_h = -60.0 (mV)
    sigma_h = -6.2 (mV)
    k_h     = 0.018 (1/ms)
    delta_h = 0.395 (1)
    tau0_h  = 0.797 (ms)
    gbar    = 0.0 (S/cm2)
    q10     = 2.3 (1)
    temp    = 23 (degC)
}

ASSIGNED {
    v        (mV)     : membrane voltage
    i        (mA/cm2) : current density
    ina      (mA/cm2) : current density of na ion
    gna      (S/cm2)  : conductance of na ion
    ena      (mV)     : reversal potential of na ion
    
    m_inf    (1)      : steady state value of m
    tau_m    (ms)     : time constant of m
    
    h_inf    (1)      : steady state value of h
    tau_h    (ms)     : time constant of h
    
    tadj     (1)      : temperature adjustment factor
    celsius  (degC)   : simulation temperature in celsius
}

STATE { m h }

BREAKPOINT {
    SOLVE states METHOD cnexp
    gna = tadj * gbar * pow(m, 3) * h
    i = gna * (v - ena) 
    ina = i
}

DERIVATIVE states {
    rates(v)
    m' = (m_inf - m) / tau_m
    h' = (h_inf - h) / tau_h
    
}

INITIAL {
    tadj = q10^((celsius - temp)/10(degC))
    rates(v)
    m = m_inf
    h = h_inf
    
}


FUNCTION alpha_prime(v (mV), k (1/ms), delta (1), vhalf (mV), sigma (mV)) (1/ms) {
    alpha_prime = k * exp(delta * (v - vhalf) / sigma)
}

FUNCTION beta_prime(v (mV), k (1/ms), delta (1), vhalf (mV), sigma (mV)) (1/ms) {
    beta_prime = k * exp(-(1 - delta) * (v - vhalf) / sigma)
}                

PROCEDURE rates(v(mV)) {
    LOCAL alpha_m, beta_m, alpha_h, beta_h

    
    m_inf = 1 / (1 + exp(-(v - vhalf_m) / sigma_m))
    alpha_m = alpha_prime(v, k_m, delta_m, vhalf_m, sigma_m)
    beta_m = beta_prime(v, k_m, delta_m, vhalf_m, sigma_m)
    tau_m = (1 / (alpha_m + beta_m) + tau0_m) / tadj
    
    h_inf = 1 / (1 + exp(-(v - vhalf_h) / sigma_h))
    alpha_h = alpha_prime(v, k_h, delta_h, vhalf_h, sigma_h)
    beta_h = beta_prime(v, k_h, delta_h, vhalf_h, sigma_h)
    tau_h = (1 / (alpha_h + beta_h) + tau0_h) / tadj
    
    
}

