TITLE Calcium-dependent potassium channel

COMMENT
26 Ago 2002 Modification of original channel to allow variable time step and to correct an initialization error.
    Done by Michael Hines(michael.hines@yale.e) and Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational Neuroscience. Obidos, Portugal

kca.mod

Calcium-dependent potassium channel
Based on
Pennefather (1990) -- sympathetic ganglion cells
taken from
Reuveni et al (1993) -- neocortical cells

Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu	
ENDCOMMENT

NEURON {
	SUFFIX KCa
	USEION k READ ek WRITE ik
	USEION ca READ cai
	RANGE gbar, ik
}

UNITS {
	(mA)    = (milliamp)
	(mV)    = (millivolt)
	(S)     = (siemens)
	(molar) = (1/liter)
	(mM)    = (millimolar)
} 

PARAMETER {
	gbar = 0.0  (S/cm2)  
	caix = 1    (1)     : Hill coefficient						
	Ra   = 0.01 (/ms)   : max act rate  
	Rb   = 0.02 (/ms)   : max deact rate 
	temp = 23   (degC)  : original temp 	
	q10  = 2.3  (1)	    : temperature sensitivity
} 


ASSIGNED {
	v       (mV)
	cai     (mM)
	ik      (mA/cm2)
	gk      (S/cm2)
	ek      (mV)
	ninf    (1)
	ntau    (ms)	
	tadj    (1)
	celsius (degC)
}
 

STATE { n }

BREAKPOINT {
	SOLVE states METHOD cnexp
	gk = tadj * gbar * n
	ik = gk * (v - ek)
} 

DERIVATIVE states { 
	rates(cai)
	n' = (ninf - n) / ntau
}

INITIAL { 
	rates(cai)
	n = ninf
}

PROCEDURE rates(cai (mM)) {  
	LOCAL alpn, betn

	tadj = q10^((celsius - temp)/10(degC))

	alpn = Ra * (1(/mM)*cai)^caix
	betn = Rb

	ntau = 1 / (tadj * (alpn + betn))
	ninf = alpn / (alpn + betn)
}












