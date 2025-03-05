TITLE V-g K+ channel (Muscarinic or M-Type?)

COMMENT
26 Ago 2002 Modification of original channel to allow variable time step and to correct an initialization error.
    Done by Michael Hines(michael.hines@yale.e) and Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational Neuroscience. Obidos, Portugal

km.mod

Potassium channel, Hodgkin-Huxley style kinetics
Based on I-M (muscarinic K channel)
Slow, noninactivating

Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu
ENDCOMMENT

NEURON {
	SUFFIX Km
	USEION k READ ek WRITE ik
	RANGE gbar, i, v12, q
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(S)  = (siemens)
	(um) = (micron)
} 

PARAMETER {
	gbar = 0.0   (S/cm2)  : 0.03 mho/cm2                          
	Ra   = 0.001 (/mV/ms) : max act rate                          
	Rb   = 0.001 (/mV/ms) : max deact rate                        
	v12  = -30   (mV)     : v 1/2 for inf                         
	q    = 9     (mV)	  : inf slope		                           
	temp = 23    (degC)   : original temp 	                       
	q10  = 2.3   (1)      : temperature sensitivity               
} 


ASSIGNED {
	v       (mV)
	ik      (mA/cm2)
	i       (mA/cm2)
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
	i = gk * (v - ek)
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

FUNCTION rateconst(v (mV), r (/mV/ms), th (mV), q (mV)) (/ms) {
	rateconst = r * (v - th) / (1 - exp(-(v - th)/q))
}

PROCEDURE rates(v (mV)) {

	LOCAL alpn, betn

	tadj = q10^((celsius - temp)/10(degC))

    :alpn = Ra * (v - v12) / (1 - exp(-(v - v12)/q))
	alpn = rateconst(v, Ra, v12, q)
    :betn = -Rb * (v - v12) / (1 - exp((v - v12)/q))
	betn = rateconst(v, -Rb, v12, -q)

    ntau = 1 / tadj/(alpn + betn)
	ninf = alpn / (alpn + betn)
}

