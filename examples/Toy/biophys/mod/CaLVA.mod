TITLE T-type Ca channel 

COMMENT
ca.mod to lead to thalamic ca current inspired by destexhe and huguenrd
Uses fixed eca instead of GHK eqn
changed from (AS Oct0899)
changed for use with Ri18  (B.Kampa 2005)
ENDCOMMENT

NEURON {
	SUFFIX CaLVA
	USEION ca READ eca WRITE ica
	RANGE gbar, ica
}

UNITS {
	(mA)    = (milliamp)
	(mV)    = (millivolt)
	(S)     = (siemens)
} 

PARAMETER {
	gbar = 0.0 (S/cm2)
	v12m = 50  (mV)
	v12h = 78  (mV)
	vwm  = 7.4 (mV)
	vwh  = 5.0 (mV)
	am   = 3   (ms)
	ah   = 85  (ms)
	vm1  = 25  (mV)
	vm2  = 100 (mV)
	vh1  = 46  (mV)
	vh2  = 405 (mV)
	wm1  = 20  (mV)
	wm2  = 15  (mV)
	wh1  = 4   (mV)
	wh2  = 50  (mV)
}

ASSIGNED {
	v       (mV)
	ica     (mA/cm2)
	gca     (S/cm2)
	eca	    (mV)
	minf    (1)
	hinf    (1)
	mtau    (ms)	
	htau    (ms)
}
 

STATE { m h }

BREAKPOINT {
	SOLVE states METHOD cnexp
	gca = gbar * pow(m,2) * h
	ica = gca * (v - eca)
}

DERIVATIVE states {
	rates(v)
	m' = (minf - m)/mtau
	h' = (hinf - h)/htau
}

INITIAL { 
	rates(v)
	m = minf
	h = hinf
}

PROCEDURE rates(v (mV)) {  

	minf = 1.0 / ( 1 + exp(-(v + v12m) / vwm) )
	hinf = 1.0 / ( 1 + exp((v + v12h) / vwh) )

	mtau = am + 1.0(ms) / ( exp((v + vm1) / wm1) + exp(-(v + vm2) / wm2))  
	htau = ah + 1.0(ms) / ( exp((v + vh1) / wh1) + exp(-(v + vh2) / wh2))  
}

