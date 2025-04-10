TITLE  Na persistent channel

COMMENT
used in distal oblique dendrites to assist Ca spike initiation  
a typo in the exponential function was pointed out by Michele Migliore and
corrected by Yiota Poirazi on December 4th, 2003
ENDCOMMENT

NEURON {
	SUFFIX nap
	USEION na READ ena WRITE ina
    RANGE  gbar, vhalf, K, i
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {                         : parameters that can be entered when function is called in cell-setup 
	gbar = 0       (mho/cm2)      : initialized conductance
	K = 4.5        (1)      : slope of steady state variable
	vhalf  = -50.4 (mV)      : half potential
}	

ASSIGNED {
	v    (mV)
	g    (mho/cm2)
	ena  (mV)
	i    (mA/cm2)
	ina  (mA/cm2)
	ninf (1)
	ntau (ms)
}

STATE { n }

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * n * n * n
	i = g * (v - ena)
	ina = i
}

DERIVATIVE states {
	rates(v)
	n' = (ninf - n)/ntau
}

INITIAL {
	rates(v)
	n = ninf
}

PROCEDURE rates(v) {    
	ninf = 1 / (1 + exp((vhalf - v)/K)) : steady state value
	ntau = 1
}