TITLE L-type calcium channel with low threshold for activation

COMMENT
used in somatic and proximal dendritic regions 
it calculates I_Ca using channel permeability instead of conductance
ENDCOMMENT

NEURON {
	SUFFIX cal
	USEION ca READ eca, cai, cao WRITE ica
        RANGE gbar, g, i
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}



PARAMETER {
	gbar = 0     (mho/cm2)
	ki  = 0.001     (mM)  
        tfa = 5                   : time constant scaling factor
}

ASSIGNED {
        v       (mV)
        g       (mho/cm2)
        eca     (mV)
        cai     (mM) : internal Ca++ concentration
        cao     (mM) : external Ca++ concentration
        i       (mA/cm2)
        ica     (mA/cm2)
        minf    (1)
        taum    (ms)
        celsius	(degC)
        }


STATE {	m }                      : unknown parameter to be solved in the DEs 


BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * m * h2(cai) : maximum channel permeability
	i = g * ghk(v, cai, cao): calcium current induced by this channel
        ica = i
}

DERIVATIVE states {
        rates(v)
        m' = (minf-m)/taum
}

INITIAL {
        rates(v)
        m = minf
}


FUNCTION h2(cai(mM)) {
	h2 = ki/(ki+cai)
}

FUNCTION ghk(v(mV), ci(mM), co(mM)) (mV) {
        LOCAL nu,f
        f = KTF(celsius)/2
        nu = v/f
        ghk=-f*(1. - (ci/co)*exp(nu))*efun(nu)
}

FUNCTION KTF(celsius (degC)) (mV) { : temperature-dependent adjustment factor
        KTF = ((25./293.15)*(celsius + 273.15))
}

FUNCTION efun(z) {
	if (fabs(z) < 1e-4) {
		efun = 1 - z/2
	}else{
		efun = z/(exp(z) - 1)
	}
}

FUNCTION alpm(v(mV)) {
	alpm = 0.055*(-27.01 - v)/(exp((-27.01-v)/3.8) - 1)
}


FUNCTION betm(v(mV)) {
        betm =0.94*exp((-63.01-v)/17)
}


PROCEDURE rates(v (mV)) {
        LOCAL a, b
        a = alpm(v)
        b = betm(v)
        minf = a / (a + b)       : estimation of activation steady state value
        taum = 1 / (tfa * (a + b)) : estimation of activation tau
        
}



