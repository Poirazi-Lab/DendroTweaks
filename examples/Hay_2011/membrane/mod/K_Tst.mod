




NEURON	{
	SUFFIX K_Tst
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
	hInf
	hTau    (ms)
}

STATE	{
	m
	h
}

BREAKPOINT	{
	SOLVE states METHOD cnexp
	g = gbar*(m^4)*h
	ik = g*(v-ek)
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
  LOCAL qt
  qt = 2.3^((34-21)/10)

	
		v = v + 10
		mInf =  1/(1 + exp(-(v+0)/19))
		mTau =  (0.34+0.92*exp(-((v+71)/59)^2))/qt
		hInf =  1/(1 + exp(-(v+66)/-10))
		hTau =  (8+49*exp(-((v+73)/23)^2))/qt
		v = v - 10
	
}
