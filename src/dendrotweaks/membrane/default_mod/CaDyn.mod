NEURON {
    SUFFIX CaDyn
    USEION ca READ ica, cai WRITE cai
    RANGE depth, tau, cainf, gamma
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
    tau = 80       (ms)    : Time constant for calcium removal
    cainf = 1e-4   (mM)    : Steady-state calcium concentration
    gamma = 0.05           : Fraction of free calcium (not buffered)
}

STATE { ca (mM) }

ASSIGNED {
    ica           (mA/cm2)
    drive_channel (mM/ms)
    cai           (mM)
}

INITIAL {
    ca = cainf
    cai = ca
}

BREAKPOINT {
    SOLVE state METHOD cnexp
}

DERIVATIVE state { 
    drive_channel = - (10000) * (ica * gamma) / (2 * FARADAY * depth)

    if (drive_channel <= 0.) { 
        drive_channel = 0. 
    }   : Prevent inward pumping

    ca' = drive_channel - (ca - cainf) / tau
    cai = ca
}
