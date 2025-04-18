


NEURON	{
	SUFFIX CaHVA
	USEION ca READ eca WRITE ica
	RANGE gbar, g, ica 
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
	eca	(mV)
	ica	(mA/cm2)
	g	(S/cm2)
	mInf    (1)
	mTau    (ms)
	mAlpha  (1)
	mBeta   (1)
	hInf    (1)
	hTau    (ms)
	hAlpha  (1)
	hBeta   (1)
}

STATE	{ 
	m
	h
}

BREAKPOINT	{
	SOLVE states METHOD cnexp
	g = gbar*m*m*h
	ica = g*(v-eca)
}

DERIVATIVE states	{
	rates()
	m' = (mInf-m)/mTau
	h' = (hInf-h)/hTau
}

INITIAL{
	rates()
	m = mInf
	h = hInf
}

PROCEDURE rates(){
	
        if((v == -27) ){        
            v = v+0.0001
        }
		mAlpha =  (0.055*(-27-v))/(exp((-27-v)/3.8) - 1)        
		mBeta  =  (0.94*exp((-75-v)/17))
		mInf = mAlpha/(mAlpha + mBeta)
		mTau = 1/(mAlpha + mBeta)
		hAlpha =  (0.000457*exp((-13-v)/50))
		hBeta  =  (0.0065/(exp((-v-15)/28)+1))
		hInf = hAlpha/(hAlpha + hBeta)
		hTau = 1/(hAlpha + hBeta)
	
}
