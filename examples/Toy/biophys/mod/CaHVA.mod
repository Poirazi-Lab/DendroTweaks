TITLE HVA Ca current

COMMENT
26 Ago 2002 Modification of original channel to allow variable time step and to correct an initialization error.
    Done by Michael Hines(michael.hines@yale.e) and Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational Neuroscience. Obidos, Portugal

ca.mod
Uses fixed eca instead of GHK eqn

HVA Ca current
Based on Reuveni, Friedman, Amitai and Gutnick (1993) J. Neurosci. 13:
4609-4621.

Author: Zach Mainen, Salk Institute, 1994, zach@salk.edu
ENDCOMMENT

NEURON {
	SUFFIX CaHVA
	USEION ca READ eca WRITE ica
	RANGE gbar, ica
}

UNITS {
	(mA)    = (milliamp)
	(mV)    = (millivolt)
	(S)     = (siemens)
}

PARAMETER {
	gbar  = 0.0      (S/cm2)
	Rma   = 0.5      (/mV/ms)
	Rmb   = 0.1      (/ms)
	v12ma = -27      (mV)
	v12mb = -75      (mV)
	qma   = 3.8      (mV)
	qmb   = 17       (mV)

	Rha   = 0.000457 (/ms)
	Rhb   = 0.0065   (/ms)
	v12ha = -13      (mV)
	v12hb = -15      (mV)
	qha   = 50       (mV)
	qhb   = 28       (mV)

	temp  = 23       (degC)  : original temp 
	q10   = 2.3      (1)     : temperature sensitivity
}

ASSIGNED {
	v       (mV)
	ica     (mA/cm2)
	gca     (S/cm2)
	eca     (mV)
	minf    (1)
	hinf    (1)
	mtau    (ms)
	htau    (ms)
	tadj    (1)
	celsius (degC)
}
 

STATE { m h }

BREAKPOINT {
	SOLVE states METHOD cnexp
	gca = tadj * gbar * pow(m,2) * h
	ica = gca * (v - eca)
} 

DERIVATIVE states {
        rates(v)   
        m' =  (minf-m)/mtau
        h' =  (hinf-h)/htau
}

INITIAL { 
	rates(v)
	m = minf
	h = hinf
}

FUNCTION f_lexp(v (mV), R (/mV/ms) , v12 (mV), q (mV)) (/ms) {
	LOCAL dv 
	dv = -(v - v12)
	f_lexp = R * dv / (exp(dv / q) - 1)
}

FUNCTION f_exp(v(mV), R(/ms), v12(mV), q(mV)) (/ms) {
	LOCAL dv
	dv = -(v - v12)
	f_exp = R * exp(dv / q)
}

FUNCTION f_sigm(v(mV), R(/ms), v12(mV), q(mV)) (/ms) {
	LOCAL dv
	dv = -(v - v12)
	f_sigm = R / (1 + exp(dv / q))
}

PROCEDURE rates(vm (mV)) {  
	LOCAL  alpm, betm, alph, beth

	tadj = q10^((celsius - temp) / 10(degC))

	
	alpm = f_lexp(vm, Rma, v12ma, qma)
	
	betm = f_exp(vm, Rmb, v12mb, qmb)
	
	mtau = 1 / (tadj * (alpm + betm))
	minf = alpm / (alpm + betm)

	
	alph = f_exp(vm, Rha, v12ha, qha)
	
	beth = f_sigm(vm, Rhb, v12hb, qhb)

	htau = 1 / ( tadj * (alph + beth))
	hinf = alph / (alph + beth)
}
