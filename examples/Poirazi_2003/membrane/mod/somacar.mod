TITLE Ca R-type channel with medium threshold for activation

COMMENT
used in somatic regions. It has lower threshold for activation/inactivation
and slower activation time constant
than the same mechanism in dendritic regions
uses channel conductance (not permeability)
written by Yiota Poirazi on 3/12/01 poirazi@LNC.usc.edu
ENDCOMMENT

NEURON {
	SUFFIX somacar
	USEION ca READ cai, cao WRITE ica
    RANGE gbar, g, i
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	FARADAY = (faraday) (coulomb)
	R = (k-mole) (joule/degC)
}

PARAMETER {
    gbar = 0      (mho/cm2) : initialized conductance
}

STATE {	m h }   : unknown activation and inactivation parameters to be solved in the DEs

ASSIGNED {
	v               (mV)
 	g 			 (mho/cm2)
	ecar			 (mV)
	i 			 (mA/cm2)
	ica (mA/cm2)
    minf (1)
	hinf (1)
	mtau (ms)
	htau (ms)
	cai (mM)
	cao (mM)
	celsius         (degC)
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * m * m * m * h
	ecar = (1e3) * (R*(celsius+273.15))/(2*FARADAY) * log (cao/cai)
	i = g * (v - ecar)
	ica = i
	}

DERIVATIVE states {
	rates(v)
	m' = (minf - m) / mtau
	h' = (hinf - h) / htau
}

INITIAL {
	rates(v)
	m = minf
	h = hinf
}

PROCEDURE rates(v) {

	minf = 1 / (1 + exp((v + 60)/(-3))) :Ca activation
	hinf = 1 / (1 + exp((v + 62)/(1)))   :Ca inactivation
	mtau = 100  : activation variable time constant
	htau = 5    : inactivation variable time constant
}