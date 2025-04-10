TITLE  H-current that uses Na ions

NEURON {
	SUFFIX h   
	NONSPECIFIC_CURRENT i
	:USEION na READ ena WRITE ina   
	RANGE gbar, i, vhalf, K, e

}

UNITS {
	(um) = (micrometer)
	(mA) = (milliamp)
	(uA) = (microamp)
	(mV) = (millivolt)
	(pmho) = (picomho)
	(mmho) = (millimho)
}

PARAMETER {
	
	gbar   = 0.0     (mho/cm2)  : initialize conductance to zero
    e     = -10   (mV)
	K      = 8.5   (mV)
	vhalf  = -90   (mV)       : half potential
}	


STATE {                : the unknown parameters to be solved in the DEs
	n
}

ASSIGNED {             : parameters needed to solve DE
	v    (mV)
	:ina  (mA/cm2)
	:ena  (mV)
	i    (mA/cm2)
	ninf (1)
	taun (ms)
	g    (mho/cm2)
}

        


INITIAL {               : initialize the following parameter using states()
	rates(v)	
	n = ninf
}


BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * n
	i = g * (v - e)  
	:ina = i
}

DERIVATIVE states {
	rates(v)
    n' = (ninf - n)/taun
}

PROCEDURE rates(v (mV)) {
 
	ninf = 1 - (1 / (1 + exp((vhalf - v)/K)))                  :steady state value

 	if (v > -30) {
		taun = 1
	} else {
		taun = 2*(1/(exp((v+145)/-17.5)+exp((v+16.8)/16.5)) + 5) :h activation tau
	}

}



