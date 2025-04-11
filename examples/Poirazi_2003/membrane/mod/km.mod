TITLE Km channel

COMMENT
km.mod
Potassium channel, Hodgkin-Huxley style kinetics
Based on I-M (muscarinic K channel)
Slow, noninactivating
Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu
	
ENDCOMMENT

NEURON {
	SUFFIX km
	USEION k READ ek WRITE ik
	RANGE i, g, gbar
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

PARAMETER {
	gbar = 0 (pS/um2)	: 0.03 mho/cm2
	tha  = -30	(mV)		: v 1/2 for inf
	qa   = 9	(mV)		: inf slope		
	Ra   = 0.001	(/ms)		: max act rate  (slow)
	Rb   = 0.001	(/ms)		: max deact rate  (slow)
	temp = 23	(degC)		: original temp 	
	q10  = 2.3			: temperature sensitivity
} 


ASSIGNED {
	v 		(mV)
	a		(/ms)
	b		(/ms)
	i 	(mA/cm2)
	ik 		(mA/cm2)
	g		(pS/um2)
	ek		(mV)
	ninf (1)
	ntau (ms)	
	tadj (1)
	celsius		(degC)
}
 

STATE { n }

BREAKPOINT {
    SOLVE states METHOD cnexp
	g = tadj * gbar * n
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


PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
	tadj = q10^((celsius - temp)/10)
	
    a = Ra * (v - tha) / (1 - exp(-(v - tha) / qa))

    b = -Rb * (v - tha) / (1 - exp((v - tha) / qa))

    ntau = 1 / (a + b)
	ninf = a * ntau

}

