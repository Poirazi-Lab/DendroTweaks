


NEURON	{
	SUFFIX Im
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
	mInf
	mTau    (ms)
	mAlpha
	mBeta
}

STATE	{ 
	m
}

BREAKPOINT	{
	SOLVE states METHOD cnexp
	g = gbar*m
	ik = g*(v-ek)
}

DERIVATIVE states	{
	rates(v)
	m' = (mInf-m)/mTau
}

INITIAL{
	rates(v)
	m = mInf
}

PROCEDURE rates(v(mV)){
  LOCAL qt
  qt = 2.3^((34-21)/10)

	
		mAlpha = 3.3e-3*exp(2.5*0.04*(v - -35))
		mBeta = 3.3e-3*exp(-2.5*0.04*(v - -35))
		mInf = mAlpha/(mAlpha + mBeta)
		mTau = (1/(mAlpha + mBeta))/qt
	
}
