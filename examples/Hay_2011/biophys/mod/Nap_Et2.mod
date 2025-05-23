




NEURON	{
	SUFFIX Nap_Et2
	USEION na READ ena WRITE ina
	RANGE gbar, g, ina
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
	ena	(mV)
	ina	(mA/cm2)
	g	(S/cm2)
	mInf
	mTau    (ms)
	mAlpha
	mBeta
	hInf
	hTau    (ms)
	hAlpha
	hBeta
}

STATE	{
	m
	h
}

BREAKPOINT	{
	SOLVE states METHOD cnexp
	g = gbar*m*m*m*h
	ina = g*(v-ena)
}

DERIVATIVE states	{
	rates(v)
	m' = (mInf-m)/mTau
	h' = (hInf-h)/hTau
}

INITIAL{
	rates(v)
	m = mInf
	h = hInf
}

PROCEDURE rates(v(mV)){
  LOCAL qt
  qt = 2.3^((34-21)/10)

	
		mInf = 1.0/(1+exp((v- -52.6)/-4.6))
    if(v == -38){
    	v = v+0.0001
    }
		mAlpha = (0.182 * (v- -38))/(1-(exp(-(v- -38)/6)))
		mBeta  = (0.124 * (-v -38))/(1-(exp(-(-v -38)/6)))
		mTau = 6*(1/(mAlpha + mBeta))/qt

  	if(v == -17){
   		v = v + 0.0001
  	}
    if(v == -64.4){
      v = v+0.0001
    }

		hInf = 1.0/(1+exp((v- -48.8)/10))
    hAlpha = -2.88e-6 * (v + 17) / (1 - exp((v + 17)/4.63))
    hBeta = 6.94e-6 * (v + 64.4) / (1 - exp(-(v + 64.4)/2.63))
		hTau = (1/(hAlpha + hBeta))/qt
	
}
