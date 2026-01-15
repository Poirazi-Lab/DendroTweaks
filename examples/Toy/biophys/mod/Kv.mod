TITLE Kv_Park_ref

COMMENT
26 Ago 2002 Modification of original channel to allow variable time step and to correct an initialization error.
    Done by Michael Hines(michael.hines@yale.e) and Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational Neuroscience. Obidos, Portugal

kv.mod

Potassium channel, Hodgkin-Huxley style kinetics
Kinetic rates based roughly on Sah et al. and Hamill et al. (1991)

Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu	
ENDCOMMENT

NEURON {
	SUFFIX Kv
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
	gbar = 0.0   (S/cm2)                                                                                      
	Ra   = 0.02  (/mV/ms) : max act rate                                                                      
	Rb   = 0.006 (/mV/ms) : max deact rate	0.002 before. Changed to 0.006                                    
	v12  = 25    (mV)	  : v 1/2 for inf                                                                       
	q    = 9     (mV)     : inf slope                                                                           
	temp = 23    (degC)   : original temp                                                                     
	q10  = 2.3   (1)	  : temperature sensitivity                                                              
} 

ASSIGNED {
	v       (mV)
	i 	    (mA/cm2)
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
	i = gk * (v - ek)
	ik = i
} 

DERIVATIVE  states {   
        rates()
        n' =  (ninf - n)/ntau
}

INITIAL { 
	rates()
	n = ninf
}


FUNCTION rateconst(v (mV), r (/mV/ms), th (mV), q (mV)) (/ms) {
	rateconst = r * (v - th) / (1 - exp(-(v - th)/q))
}

PROCEDURE rates() {

	LOCAL alpn, betn

	tadj = q10^((celsius - temp)/10(degC))

	alpn = rateconst(v, Ra, v12, q)
	betn = rateconst(v, -Rb, v12, -q)

    ntau = 1 / (tadj * (alpn + betn))
	ninf = alpn/(alpn + betn)
}