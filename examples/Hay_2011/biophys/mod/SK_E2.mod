: SK-type calcium-activated potassium current
: Reference : Kohler et al. 1996

NEURON {
       SUFFIX SK_E2
       USEION k READ ek WRITE ik
       USEION ca READ cai
       RANGE gbar, gSK_E2, ik
}

UNITS {
      (mV) = (millivolt)
      (mA) = (milliamp)
      (mM) = (milli/liter)
}

PARAMETER {
          gbar = 0.0 (mho/cm2)
          zTau = 1              (ms)
}

ASSIGNED {
         v            (mV)
         ek           (mV)
         cai          (mM)
         zInf
         ik            (mA/cm2)
         gSK_E2	       (mho/cm2)
}

STATE {
      z   FROM 0 TO 1
}

BREAKPOINT {
           SOLVE states METHOD cnexp
           gSK_E2  = gbar * z
           ik   =  gSK_E2 * (v - ek)
}

DERIVATIVE states {
        rates(cai)
        z' = (zInf - z) / zTau
}

PROCEDURE rates(cai(mM)) {
          if(cai < 1e-7 (mM)){
	              cai = cai + 1e-07 (mM)
          }
          zInf = 1/(1 + (0.00043 (mM)/ cai)^4.8)
}

INITIAL {
        rates(cai)
        z = zInf
}
