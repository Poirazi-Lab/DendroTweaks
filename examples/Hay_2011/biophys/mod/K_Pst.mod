





NEURON	{
	SUFFIX K_Pst
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
	g = gbar*m*m*h
	ik = g*(v-ek)
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
	
		v = v + 10
		mInf =  (1/(1 + exp(-(v+1)/12)))
        if(v<-50){
		    mTau =  (1.25+175.03*exp(-v * -0.026))/qt
        }else{
            mTau = ((1.25+13*exp(-v*0.026)))/qt
        }
		hInf =  1/(1 + exp(-(v+54)/-11))
		hTau =  (360+(1010+24*(v+55))*exp(-((v+75)/48)^2))/qt
		v = v - 10
	
}
