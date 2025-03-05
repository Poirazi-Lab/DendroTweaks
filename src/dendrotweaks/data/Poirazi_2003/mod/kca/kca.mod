TITLE Slow Ca-dependent potassium current

COMMENT
   Ca++ dependent K+ current IC responsible for slow AHP
   Differential equations

   Model based on a first order kinetic scheme

       + n cai <->     (alpha,beta)

   Following this model, the activation fct will be half-activated at 
   a concentration of Cai = (beta/alpha)^(1/n) = cac (parameter)

   The mod file is here written for the case n=2 (2 binding sites)
   ---------------------------------------------

   This current models the "slow" IK[Ca] (IAHP): 
      - potassium current
      - activated by intracellular calcium
      - NOT voltage dependent

   A minimal value for the time constant has been added

   Ref: Destexhe et al., J. Neurophysiology 72: 803-818, 1994.
   See also: http://www.cnl.salk.edu/~alain , http://cns.fmed.ulaval.ca
   modifications by Yiota Poirazi 2001 (poirazi@LNC.usc.edu)
   taumin = 0.5 ms instead of 0.1 ms	

   activation kinetics are assumed to be at 22 deg. C
   Q10 is assumed to be 3     
ENDCOMMENT

NEURON {
        SUFFIX kca
        USEION k READ ek WRITE ik
        USEION ca READ cai
        RANGE gbar, g, i
}


UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
        (molar) = (1/liter)
        (mM) = (millimolar)
}


PARAMETER {
        gbar    = 0.0   (mho/cm2)
        beta    = 0.03   (1/ms)          : backward rate constant
        cac     = 0.025  (mM)            : middle point of activation fct
        taumin  = 0.5    (ms)            : minimal value of the time cst
        }


STATE { m }        : activation variable to be solved in the DEs       

ASSIGNED {      
        v       (mV)
        g       (mho/cm2)
        ek      (mV)
        cai     (mM)
        i       (mA/cm2)
        ik      (mA/cm2)
        m_inf   (1)                     
        tau_m   (ms)
        tadj    (1)
        celsius (degC)
}
BREAKPOINT { 
        SOLVE states METHOD cnexp
        g = gbar * m * m * m     
        i = g * (v - ek)
        ik = i
}

DERIVATIVE states { 
        rates(v, cai)
        m' = (m_inf - m) / tau_m
}

INITIAL {
        rates(v, cai)
        m = m_inf
}

PROCEDURE rates(v(mV), cai(mM)) {  LOCAL car
        
        tadj = 3 ^ ((celsius-22.0)/10) 

        car = (cai / cac)^2
        m_inf = car / ( 1 + car )      : activation steady state value
        tau_m =  1 / beta / (1 + car) / tadj
        if (tau_m < taumin) { tau_m = taumin }   : activation min value of time cst
}

