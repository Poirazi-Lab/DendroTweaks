TITLE Decay of internal calcium concentration

NEURON {
    SUFFIX CaDyn
    USEION ca READ ica, cai WRITE cai
    RANGE depth, taur, cainf, gamma, kt, kd
}

UNITS {
    (molar) = (1/liter)          : moles do not appear in units
    (mM)    = (millimolar)
    (um)    = (micron)
    (mA)    = (milliamp)
    (msM)   = (ms mM)
    FARADAY = (faraday) (coulomb)
}

PARAMETER {
    depth = 0.1    (um)    : Depth of calcium shell
    taur = 700     (ms)    : Time constant for calcium removal
    cainf = 1e-8   (mM)    : Steady-state calcium concentration
    gamma = 1              : Fraction of free calcium (not buffered)
    kt = 1         (mM/ms) : Michaelis-Menten rate (not used by default)
    kd = 5e-4      (mM)    : Michaelis-Menten dissociation constant (not used by default)
}

STATE { cai (mM) }

ASSIGNED {
    ica           (mA/cm2)
    drive_channel (mM/ms)
    drive_pump    (mM/ms)
}

INITIAL {
    cai = cainf
}

BREAKPOINT {
    SOLVE state METHOD cnexp
}

DERIVATIVE state { 
    drive_channel = - (10000) * (ica * gamma) / (2 * FARADAY * depth)

    if (drive_channel <= 0.) { 
        drive_channel = 0. 
    }   : Prevent inward pumping

    drive_pump = - kt * cai / (cai + kd) : Michaelis-Menten removal

    cai' = drive_channel + drive_pump + (cainf - cai) / taur
    
}