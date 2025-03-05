TITLE Ca R-type channel with medium threshold for activation

COMMENT
used in distal dendritic regions, together with calH.mod, to help
the generation of Ca++ spikes in these regions
uses channel conductance (not permeability)
written by Yiota Poirazi on 11/13/00 poirazi@LNC.usc.edu
ENDCOMMENT

NEURON {
	SUFFIX car
	USEION ca READ eca WRITE ica
    RANGE gbar, g, i
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
    gbar = 0      (mho/cm2) 
}  

ASSIGNED {      
	v (mV)
	g (mho/cm2)
	eca (mV)
	i (mA/cm2)	
	ica (mA/cm2)
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

DERIVATIVE states {	: exact when v held constant
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

	minf = 1 / (1 + exp((v+48.5)/(-3)))
	mtau = 50

	hinf = 1 / (1 + exp((v+53)/(1)))
	htau = 5
	
}
















