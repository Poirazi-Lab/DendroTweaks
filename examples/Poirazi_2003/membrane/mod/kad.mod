TITLE K-A channel from Klee Ficker and Heinemann
: modified by Brannon and Yiota Poirazi (poirazi@LNC.usc.edu) 
: to account for Hoffman et al 1997 distal region kinetics
: used only in locations > 100 microns from the soma

NEURON {
	SUFFIX kad
	USEION k READ ek WRITE ik
        RANGE gbar, g, i
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}



PARAMETER {                        :parameters that can be entered when function is called in cell-setup   
        
	gbar = 0      (mho/cm2)  :initialized conductance
        
        vhalfn = -1     (mV)       :activation half-potential
        vhalfl = -56    (mV)       :inactivation half-potential
        a0n = 0.1       (/ms)      :parameters used
        zetan = -1.8    (1)        :in calculation of
        zetal = 3       (1)        :steady state values
        gmn   = 0.39    (1)        :and time constants
        gml   = 1       (1)
	lmin  = 2       (mS)
	nmin  = 0.1     (mS)
	pw    = -1      (1)
	tq    = -40
	qq    = 5
	q10   = 5                  :temperature sensitivity
}



STATE {       :the unknown parameters to be solved in the DEs 
	n l
}

ASSIGNED {    :parameters needed to solve DE
	ik (mA/cm2)
        ek (mV)
        v (mV)
        celsius (degC)
        i (mA/cm2)
        ninf (1)
        linf     (1)  
        taul (ms)
        taun (ms)
        g (mho/cm2)
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * n * l
	i = g * (v - ek)
        ik = i
}

DERIVATIVE states {   : solve the DEs
        rates(v)         : update the parameters ninf, linf, taul, taun
        n' = (ninf - n)/taun
        l' = (linf - l)/taul
}

INITIAL {    :initialize the following parameter using rates()
	rates(v)
	n = ninf
	l = linf
}

FUNCTION alpn(v(mV)) { LOCAL zeta
  zeta = zetan+pw/(1+exp((v-tq)/qq))
  alpn = exp(1.e-3*zeta*(v-vhalfn)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betn(v(mV)) { LOCAL zeta
  zeta = zetan+pw/(1+exp((v-tq)/qq))
  betn = exp(1.e-3*zeta*gmn*(v-vhalfn)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION alpl(v(mV)) {
  alpl = exp(1.e-3*zetal*(v-vhalfl)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betl(v(mV)) {
  betl = exp(1.e-3*zetal*gml*(v-vhalfl)*9.648e4/(8.315*(273.16+celsius))) 
}


PROCEDURE rates(v (mV)) {		 :callable from hoc
        LOCAL a,qt

        qt = q10^((celsius-24)/10)       : temprature adjastment factor

        a = alpn(v)
        ninf = 1/(1 + a)		 : activation variable steady state value
        taun = betn(v)/(qt*a0n*(1+a))	 : activation variable time constant
	if (taun<nmin) {taun=nmin}	 : time constant not allowed to be less than nmin
        
        a = alpl(v)
        linf = 1/(1+ a)                  : inactivation variable steady state value
	taul = 0.26*(v+50)               : inactivation variable time constant
	if (taul<lmin) {taul=lmin}       : time constant not allowed to be less than lmin
        
}
