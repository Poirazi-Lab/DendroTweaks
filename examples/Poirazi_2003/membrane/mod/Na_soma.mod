TITLE NaV somatic Na+ channel from Poirazi et al. 2003 hh mechanism

NEURON {
	SUFFIX Na_soma
	USEION na READ ena WRITE ina
	RANGE gbar, g, i, ar2
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(S)  = (siemens)
}


PARAMETER {                     :parameters that can be entered when function is called in cell-setup
	gbar = 0   (S/cm2)  :initialized conductances
    a0r = 0.0003 (ms)
    b0r = 0.0003 (ms)
    zetar = 12
    gmr = 0.2
	ar2 = 1.0               :initialized parameter for location-dependent
                                :Na-conductance attenuation, "s", (ar=1 -> zero attenuation)
	taumin = 3   (ms)       :min activation time for "s" attenuation system
    vvs  = 2     (mV)       :slope for "s" attenuation system
    vhalfr = -60 (mV)       :half potential for "s" attenuation system
    
}

STATE {				:the unknown parameters to be solved in the DEs
	m h s
}

ASSIGNED {			:parameters needed to solve DE
	v            (mV)
	i 		  (mA/cm2)
	ina (mA/cm2)
	ena (mV)
	g (S/cm2)
	minf (1)
	mtau (ms)
	hinf (1)
	htau (ms)
	sinf (1)
	stau (ms)
	celsius (degC)
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * m * m * h * s
	i = g * (v - ena) :Sodium current
	ina = i
}

DERIVATIVE states {		:computes state variables m, h, and n
	rates(v)
	m' = (minf - m)/mtau
	h' = (hinf - h)/htau
	s' = (sinf - s)/stau
}

INITIAL {			:initialize the following parameter using states()
	rates(v)
	m = minf
	h = hinf
	s = sinf
}

FUNCTION alpv(v(mV), vh) {    :used in "s" activation system infinity calculation
	alpv = (1+ar2*exp((v-vh)/vvs))/(1+exp((v-vh)/vvs))
}

FUNCTION alpr(v(mV)) {       :used in "s" activation system tau
	alpr = exp(1.e-3*zetar*(v-vhalfr)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betr(v(mV)) {       :used in "s" activation system tau
	betr = exp(1.e-3*zetar*gmr*(v-vhalfr)*9.648e4/(8.315*(273.16+celsius))) 
}

PROCEDURE rates(v (mV)) {LOCAL tmp
	
    minf = 1 / (1 + exp((v + 44)/(-3)))    :Na activation
	mtau = 0.05 

 	hinf = 1 / (1 + exp((v + 49)/(3.5)))   :Na inactivation 
	htau = 1

	sinf = alpv(v, vhalfr)
	tmp = betr(v)/(a0r + b0r * alpr(v))
	if (tmp < taumin) {tmp = taumin}
	stau = tmp   :s activation tau

}