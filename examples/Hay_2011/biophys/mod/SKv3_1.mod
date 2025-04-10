


NEURON	{
	SUFFIX SKv3_1
	USEION k READ ek WRITE ik
	RANGE gbar, g, ik 
}

UNITS	{
	(S) = (siemens)
	(mV) = (millivolt)
	(mA) = (milliamp)
}

PARAMETER	{
	gbar = 0.0 (S/cm2) 
}

ASSIGNED	{
	v	(mV)
	ek	(mV)
	ik	(mA/cm2)
	g	(S/cm2)
	mInf	(1)
	mTau	(ms)
}

STATE	{ 
	m      (1)
}

BREAKPOINT	{
	SOLVE states METHOD cnexp
	g = gbar*m
	ik = g*(v-ek)
}

DERIVATIVE states	{
	rates()
	m' = (mInf-m)/mTau
}

INITIAL{
	rates()
	m = mInf
}

PROCEDURE rates(){
		mInf =  1/(1+exp(((v -(18.700(mV)))/(-9.700(mV)))))
		mTau =  0.2*20.000(ms)/(1+exp(((v -(-46.560(mV)))/(-44.140(mV)))))
	
	
}
