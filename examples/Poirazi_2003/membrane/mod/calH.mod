TITLE Ca L-type channel with high treshold of activation

COMMENT
inserted in distal dendrites to account for distally
restricted initiation of Ca++ spikes
uses channel conductance (not permeability)
written by Yiota Poirazi, 1/8/00 poirazi@LNC.usc.edu
ENDCOMMENT

NEURON {
	SUFFIX calH
	USEION ca READ eca WRITE ica
    RANGE gbar, g, i
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
    gbar = 0 (mho/cm2) 
	}

ASSIGNED {
	v    (mV)
    g 	 (mho/cm2)
	eca	 (mV)
	i 	 (mA/cm2)
	ica  (mA/cm2)
    minf (1)
	hinf (1)
	mtau (ms)
	htau (ms)
}

STATE {	m h }

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * m * m * m * h
	i = g * (v - eca)
	ica = i
	}

DERIVATIVE states {
	rates(v)
	m' = (minf - m)/mtau
	h' = (hinf - h)/htau
}

INITIAL {
	rates(v)
	m = minf
	h = hinf
    }

PROCEDURE rates(v) {LOCAL a, b :rest = -70

	minf = 1 / (1 + exp((v + 37) / (-1)))  : Ca activation 
	hinf = 1 / (1 + exp((v + 41) / (0.5))) : Ca inactivation

	mtau = 3.6  : activation variable time constant
	htau = 29   : inactivation variable time constant
}















