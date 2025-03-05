TITLE Leak channel

COMMENT
NEURON Book Listing 9.1, 
Replaced g with gbar for consistency with other channels
Overridden the default values of gbar to 0.0 and e to -70 mV
ENDCOMMENT

NEURON {
	SUFFIX Leak
	NONSPECIFIC_CURRENT i
	RANGE i, e, gbar
}

PARAMETER {
	gbar = 0.0   (siemens/cm2)     
	e = -70   (millivolt)   
} 

ASSIGNED {
	v       (millivolt)
	i 	    (milliamp/cm2)
}

BREAKPOINT {
    i = gbar * (v - e)
}