TITLE t-type calcium channel with high threshold for activation

COMMENT
used in somatic and dendritic regions 
it calculates I_Ca using channel permeability instead of conductance
The T-current does not activate calcium-dependent currents.
The construction with dummy ion Ca prevents the updating of the 
internal calcium concentration. 
ENDCOMMENT

NEURON {
	SUFFIX cat
	USEION ca READ cai, cao WRITE ica VALENCE 2
        
        RANGE gbar, g, i
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}



PARAMETER {           :parameters that can be entered when function is called in cell-setup 

        gbar = 0   (mho/cm2)  : initialized conductance

        tBase = 23.5  (degC)
	ki = 0.001    (mM)
        tfa = 1                  : activation time constant scaling factor
        tfi = 0.68               : inactivation time constant scaling factor
}

ASSIGNED {     : parameters needed to solve DE
        v (mV) 
        cai (mM) 
        cao (mM) 
        i (mA/cm2)
	ica (mA/cm2)
        g  (mho/cm2) 
        minf (1)
        hinf (1)
        taum (ms)
        tauh (ms)
}

STATE {	m h }  : unknown activation and inactivation parameters to be solved in the DEs 


BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * m * m * h * h2(cai) : maximum channel permeability
	i = g * ghk(v, cai, cao)    : dummy calcium current induced by this channel
        ica = i
}

DERIVATIVE states { : solve the DEs
        rates(v)
        m' = (minf - m)/taum
        h' = (hinf - h)/tauh
}

INITIAL {
	rates(v)
        m = minf
        h = hinf
}


FUNCTION h2(cai(mM)) {
	h2 = ki/(ki+cai)
}

FUNCTION ghk(v(mV), ci(mM), co(mM)) (mV) { LOCAL nu,f
        f = KTF(celsius)/2
        nu = v/f
        ghk=-f*(1. - (ci/co)*exp(nu))*efun(nu)
}

FUNCTION KTF(celsius (degC)) (mV) {   : temperature-dependent adjustment factor
        KTF = ((25./293.15)*(celsius + 273.15))
}

FUNCTION efun(z) {
	if (fabs(z) < 1e-4) {
		efun = 1 - z/2
	}else{
		efun = z/(exp(z) - 1)
	}
}

FUNCTION alph(v(mV)) {
	alph = 1.6e-4*exp(-(v+57)/19)
}

FUNCTION beth(v(mV)) {
	beth = 1/(exp((-v+15)/10)+1.0)
}

FUNCTION alpm(v(mV)) {
	alpm = 0.1967*(-1.0*v+19.88)/(exp((-1.0*v+19.88)/10.0)-1.0)
}

FUNCTION betm(v(mV)) {
	betm = 0.046*exp(-v/22.73)
}



PROCEDURE rates(v (mV)) { :callable from hoc
        LOCAL a
        a = alpm(v)
        taum = 1/(tfa*(a + betm(v))) : estimation of activation tau
        minf =  a/(a+betm(v))        : estimation of activation steady state
        
        a = alph(v)
        tauh = 1/(tfi*(a + beth(v))) : estimation of inactivation tau
        hinf = a/(a+beth(v))         : estimation of inactivation steady state
        
}
