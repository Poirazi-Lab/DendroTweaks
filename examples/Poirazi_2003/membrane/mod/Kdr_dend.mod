TITLE Kdr 

COMMENT
HH channel that includes both a sodium and a delayed rectifier channel 
and accounts for sodium conductance attenuation
Bartlett Mel-modified Hodgkin - Huxley conductances (after Ojvind et al.)
Terrence Brannon-added attenuation 
Yiota Poirazi-modified Kdr and Na threshold and time constants
to make it more stable, 2000, poirazi@LNC.usc.edu
Used in all BUT somatic and axon sections. The spike threshold is about -50 mV
ENDCOMMENT

NEURON {
	SUFFIX Kdr_dend
	USEION k READ ek WRITE ik
	RANGE gbar
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
	gbar = 0    (mho/cm2)  :actual values set in cell-setup.hoc
}


ASSIGNED {			: parameters needed to solve DE
	v (mV)
	g (mho/cm2)
    ek (mV)
    i (mA/cm2)
	ik (mA/cm2)
	ninf (1)
	ntau (ms)
}

STATE {                         : the unknown parameters to be solved in the DEs
	n
}

BREAKPOINT {
	SOLVE states METHOD cnexp
    g = gbar * n * n
	i = g * (v - ek)        :Potassium current
	ik = i
}

DERIVATIVE states {            : solve the DEs
    rates(v)
    n' = (ninf - n)/ntau
}

INITIAL {                       : initialize the following parameter using states()
	rates(v)
	n = ninf
}

PROCEDURE rates(v (mV)) {
	ninf = 1 / (1 + exp((v + 42)/(-2))) :K activation
    ntau = 2.2
}