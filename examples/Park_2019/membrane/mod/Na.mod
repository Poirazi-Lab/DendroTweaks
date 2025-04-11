TITLE Na channel

COMMENT
26 Ago 2002 Modification of original channel to allow variable time
step and to correct an initialization error.
    Done by Michael Hines(michael.hines@yale.e) and Ruggero
Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational
Neuroscience. Obidos, Portugal
11 Jan 2007
    Glitch in trap where (v/th) was where (v-th)/q is. (thanks Ronald
van Elburg!)

na.mod

Sodium channel, Hodgkin-Huxley style kinetics.  

Kinetics were fit to data from Huguenard et al. (1988) and Hamill et
al. (1991)

Mainen, Z. F., Joerges, J., Huguenard, J. R., & Sejnowski, T. J. (1995). 
A model of spike initiation in neocortical pyramidal neurons. 
Neuron, 15(6), 1427–1439. doi:10.1016/0896-6273(95)90020-9
ENDCOMMENT

NEURON {
	SUFFIX Na
	USEION na READ ena WRITE ina
	RANGE gbar, i, v12m, qm, v12ha, v12hb, qh, v12hinf, qhinf, Rma, Rmb, Rhb, Rha
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(S)  = (siemens)
	(um) = (micron)
} 

FUNCTION rateconst2(v (mV), r (/mV/ms), v12 (mV), q (mV)) (/ms) {
	if (fabs((v - v12)/q) > 1e-6) {
	        rateconst2 = r * (v - v12) / (1 - exp(-(v - v12)/q))
	} else {
	        rateconst2 = r * q
 	}
}

PARAMETER {
	gbar    = 0.0    (S/cm2)
	Rma     = 0.182  (/mV/ms) : opening max rate
	Rmb     = 0.14   (/mV/ms) : closing max rate
	v12m    = -30    (mV)     : (1/2) half-activation voltage
	qm      = 9.8    (mV)     : steepness of the voltage-dependence	

	Rhb     = 0.0091 (/mV/ms) : inactivation max rate
	Rha     = 0.024  (/mV/ms) : inactivation recovovery max rate
	v12ha   = -45	 (mV)     : half-activation voltage
	v12hb   = -70	 (mV)     : half-activation voltage
	qh      = 5      (mV)     : inact tau slope
	v12hinf = -60    (mV)     : inact inf slope	
	qhinf   = 6.2	 (mV)     : inact inf slope

	temp    = 23     (degC)   : original temp 
	q10     = 2.3    (1)      : temperature sensitivity

}

ASSIGNED {
	v       (mV)
	i 	    (mA/cm2)
	ina     (mA/cm2)
	gna     (S/cm2)
	ena     (mV)
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
    gna = tadj * gbar * pow(m, 3) * h
	i = gna * (v - ena)
	ina = i
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

FUNCTION rateconst(v (mV), r (/mV/ms), v12 (mV), q (mV)) (/ms) {
	if (fabs((v - v12)/q) > 1e-6) {
	        rateconst = r * (v - v12) / (1 - exp(-(v - v12)/q))
	} else {
	        rateconst = r * q
 	}
}


PROCEDURE rates(v (mV)) {

	LOCAL alpm, betm, alph, beth

	tadj = q10^((celsius - temp)/10(degC))

	alpm = rateconst(v, Rma, v12m, qm)
	betm = rateconst(-v, Rmb, -v12m,  qm)

	alph = rateconst(v, Rha, v12ha,  qh)
	beth = rateconst(-v, Rhb, -v12hb, qh)

	mtau = 1 / (tadj * (alpm + betm))
	minf = alpm / (alpm + betm)

	htau = 1 / (tadj * (alph + beth))
	hinf = 1 / (1 + exp((v - v12hinf)/qhinf))
}
