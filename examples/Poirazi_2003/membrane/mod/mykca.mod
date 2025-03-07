TITLE CaGk

COMMENT
Calcium activated mAHP K channel.
From Moczydlowski and Latorre (1983) J. Gen. Physiol. 82

the preceding two numbers were switched on 8/19/92 in response to a bug
report by Bartlett Mel. In the paper the kinetic scheme is
C <-> CCa (K1)
CCa <-> OCa (beta2,alpha2)
OCa <-> OCa2 (K4)
In this model abar = beta2 and bbar = alpha2 and K4 comes from d2 and k2
I was forcing things into a nomenclature where alpha is the rate from
closed to open. Unfortunately I didn't switch the numbers.

if state_mykca is called from hoc, garbage or segmentation violation will
result because range variables won't have correct pointer.  This is because
only BREAK_POINT sets up the correct pointers to range variables.
ENDCOMMENT

NEURON {
	SUFFIX mykca
	USEION ca READ cai
	USEION k READ ek WRITE ik
	RANGE gbar, ik
}

UNITS {
	(molar) = (1/liter)
	(mV) =	(millivolt)
	(mA) =	(milliamp)
	(mM) =	(millimolar)
	FARADAY = (faraday) (coulombs)
	R = (k-mole) (joule/degC)
}

PARAMETER {
	gbar = 0.0	(mho/cm2)
	d1 = 0.84
	d2 = 1.0
	k1 = 0.18	(mM)
	k2 = 0.011	(mM)
	bbar = 0.28	(/ms)
	abar = 0.48	(/ms)
}


ASSIGNED {
	v		(mV)
	g 		(mho/cm2)
	ek		(mV)
	i 		(mA/cm2)
	ik		(mA/cm2)
	cai 	(mM)
	minf	(1)
	mtau	(ms)
	celsius (degC)
}

STATE {	m }		: fraction of open channels

BREAKPOINT {
	SOLVE state METHOD cnexp
	g = gbar * m
	i = g * (v - ek)
	ik = i
}

DERIVATIVE state {
	rate(v, cai)
	m' = (minf - m)/mtau
}

INITIAL {
	rate(v, cai)
	m = minf
}

FUNCTION alp(v (mV), ca (mM)) (1/ms) {
	alp = abar/(1 + exp1(k1, d1, v)/ca)
}

FUNCTION bet(v (mV), ca (mM)) (1/ms) {
	bet = bbar/(1 + ca/exp1(k2, d2, v))
}  

FUNCTION exp1(k (mM), d, v (mV)) (mM) {
	exp1 = k * exp(-2 * d * FARADAY * (0.001) * v / R / (273.15 + celsius))
}

PROCEDURE rate(v (mV), ca (mM)) {
	LOCAL a, b
	a = alp(v,ca)
	b = bet(v,ca)
	mtau = 1/(a + b)   : estimation of activation mtau
	minf = a * mtau    : estimation of activation steady state value
}
