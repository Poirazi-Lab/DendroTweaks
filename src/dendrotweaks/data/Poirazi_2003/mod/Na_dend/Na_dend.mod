TITLE HH channel that includes both a sodium and a delayed rectifier channel 
: and accounts for sodium conductance attenuation
: Bartlett Mel-modified Hodgkin - Huxley conductances (after Ojvind et al.)
: Terrence Brannon-added attenuation 
: Yiota Poirazi-modified Kdr and Na threshold and time constants
: to make it more stable, 2000, poirazi@LNC.usc.edu
: Used in all BUT somatic and axon sections. The spike threshold is about -50 mV

NEURON {
	SUFFIX Na_dend
	USEION na READ ena WRITE ina 
	RANGE gbar, g, i, ar2
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
    (S) = (siemens)
}



PARAMETER {   : parameters that can be entered when function is called in cell-setup
    gbar = 0   (S/cm2)  :initialized conductances
    a0r = 0.0003 (ms)
    b0r = 0.0003 (ms)
    zetar = 12    
	zetas = 12   
    gmr = 0.2   
	ar2 = 1.0               :initialized parameter for location-dependent
                                :Na-conductance attenuation, "s", (ar=1 -> zero attenuation)
	taumin = 3   (ms)       :min activation time for "s" attenuation system
    vvs  = 2     (mV)       :slope for "s" attenuation system
    vhalfr = -60 (mV)       :half potential for "s" attenuation system
	W = 0.016    (/mV)      :this 1/61.5 mV
    
	
	
	
}


ASSIGNED {			: parameters needed to solve DE
    v            (mV)
    i           (mA/cm2)
	ina (mA/cm2)
    g (S/cm2)
    ena          (mV)
	minf (1)
    hinf (1)
    sinf (1)
	mtau (ms)
	htau (ms)
    stau (ms)
    celsius      (degC)
}

STATE {                         : the unknown parameters to be solved in the DEs
	m h s
}


BREAKPOINT {
	SOLVE states METHOD cnexp
    g = gbar * m * m * h * s
	i = g * (v - ena)
    ina = i
}

DERIVATIVE states {   : solve the DEs
    rates(v)
    m' = (minf - m)/mtau
    h' = (hinf - h)/htau
    s' = (sinf - s)/stau
}

INITIAL {                    
	rates(v)
	m = minf
	h = hinf
    s = 1
}

FUNCTION alpv(v(mV),vh) {    :used in "s" activation system infinity calculation
  alpv = (1+ar2*exp((v-vh)/vvs))/(1+exp((v-vh)/vvs))
}

FUNCTION alpr(v(mV)) {       :used in "s" activation system tau
  alpr = exp(1.e-3*zetar*(v-vhalfr)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betr(v(mV)) {       :used in "s" activation system tau
  betr = exp(1.e-3*zetar*gmr*(v-vhalfr)*9.648e4/(8.315*(273.16+celsius))) 
}

PROCEDURE rates(v (mV)) {LOCAL tmp

    minf = 1 / (1 + exp((v + 40)/(-3))) :Na activation
    mtau = 0.05

    hinf = 1 / (1 + exp((v + 45)/(3)))  :Na inactivation
    htau = 0.5

    sinf = alpv(v,vhalfr) :s activation
    tmp = betr(v)/(a0r+b0r*alpr(v)) 
	if (tmp < taumin) {tmp = taumin}
    stau = tmp

}