TITLE Kdir somatic K+ channel from Poirazi et al. 2003 hh mechanism


NEURON {
	SUFFIX Kdr_soma
	USEION k READ ek WRITE ik
	RANGE gbar, g, i
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}


PARAMETER {                    
   gbar = 0  (mho/cm2)
}

ASSIGNED {
	v    (mV)
	i   (mA/cm2)
	ik   (mA/cm2)
	g (mho/cm2)
	ek  (mV)
	ninf (1)
	ntau (ms)
	celsius (degC)
}

STATE {
	n
}


BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * n * n
	i = g * (v - ek)
	ik = i
}

DERIVATIVE states {
	rates(v)
	n' = (ninf - n)/ntau
}

INITIAL {
	rates(v)
	n = ninf
}

PROCEDURE rates(v(mV)) {	 

	ninf = 1 / (1 + exp((v + 46.3)/(-3)))
	ntau = 3.5   
	
}