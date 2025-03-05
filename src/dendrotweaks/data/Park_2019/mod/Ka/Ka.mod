TITLE K-A channel from Klee Ficker and Heinemann

COMMENT
: modified to account for Dax A Current --- M.Migliore Jun 1997
modified to be used with cvode  M.Migliore 2001
ENDCOMMENT

NEURON {
	SUFFIX Ka
	USEION k READ ek WRITE ik
    RANGE gbar, ik
}

UNITS {
	(mA) = (milliamp)  
	(mV) = (millivolt) 
	(S)  = (siemens)   
}

PARAMETER {
	gbar   = 0.0  (S/cm2)
	vhalfn = 11   (mV)
	vhalfl = -56  (mV)
	a0l    = 0.05 (/ms)
	a0n    = 0.05 (/ms)
	zetan  = -1.5 (1)
	zetal  = 3    (1)
	gmn    = 0.55 (1)
	gml    = 1    (1)
	lmin   = 2    (mS)
	nmin   = 0.1  (mS)
	pw     = -1   (1)
	tq     = -40  
	qq     = 5    
	q10    = 5    
	qtl    = 1    
	temp   = 24   (degC) : original temperature
}

ASSIGNED {
	v       (mV)
	ik      (mA/cm2)
	gka     (S/cm2)
	ek      (mV)
	ninf    (1)
	linf    (1)  
	taul    (ms)
	taun    (ms)
	tadj    (1)
	celsius (degC)
}

STATE { n l }

BREAKPOINT {
	SOLVE states METHOD cnexp
	gka = gbar * n * l
	ik = gka * (v - ek)

}

DERIVATIVE states {
        rates(v)
        n' = (ninf - n)/taun
        l' = (linf - l)/taul
}

INITIAL {
	rates(v)
	n = ninf
	l = linf
}

FUNCTION alpn(v(mV)) (/ms) {
	LOCAL zeta
    zeta = zetan + pw / (1 + exp((v - tq) / qq))
    alpn = exp(1.e-3*zeta*(v-vhalfn)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betn(v(mV)) (/ms) {
	LOCAL zeta
  	zeta = zetan + pw / (1 + exp((v - tq)/qq))
  	betn = exp(1.e-3*zeta*gmn*(v-vhalfn)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION alpl(v(mV)) (/ms) {
	alpl = exp(1.e-3*zetal*(v-vhalfl)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betl(v(mV)) (/ms) {
	betl = exp(1.e-3*zetal*gml*(v-vhalfl)*9.648e4/(8.315*(273.16+celsius))) 
}

PROCEDURE rates(v (mV)) {
    
	LOCAL a

    tadj = q10^((celsius - temp)/10(degC))

    a = alpn(v)
    ninf = 1/(1 + a)
    taun = betn(v) / (tadj * a0n * (1 + a))
	if (taun<nmin) {
		taun = nmin
	}
    a = alpl(v)
    linf = 1 / (1 + a)
	taul = 0.26 * (v + 50) / qtl
	if (taul < lmin / qtl) {
		taul = lmin / qtl
	}
}

