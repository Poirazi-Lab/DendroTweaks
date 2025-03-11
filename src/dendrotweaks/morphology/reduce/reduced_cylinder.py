import collections
import neuron
from neuron import h
import math
import cmath

import logging
logger = logging.getLogger(__name__)

h('''obfunc lowest_impedance_recursive() { local lowest_impedance, lowest_phase, i   localobj curr_subtree_root, sref1, lowest_imp_vec, lowest_child_subtree_impedance, imp_obj
    curr_subtree_root = $o1  // in the first call to the function, this is a root section of a dendritic trunk
    imp_obj = $o2
    curr_subtree_root.sec {
        lowest_impedance = imp_obj.transfer(1) // farthest tip of the the curr root section
        lowest_phase = imp_obj.transfer_phase(1)
    }
    if (curr_subtree_root.nchild != 0) { // if the curr section has child sections
        for i=0, curr_subtree_root.nchild-1 curr_subtree_root.child[i] {  // for each child of the root, finds the lowest impedance within the subtree whose root is the curr child (in relation to the proximal tip in the curr root child)
            curr_subtree_root.child[i] sref1 = new SectionRef()
            lowest_child_subtree_impedance = lowest_impedance_recursive(sref1, imp_obj) // recursively returns the lowest transfer impedance and transfer phase within the curr subtree as a vector
            if (lowest_child_subtree_impedance.x[0] < lowest_impedance) {
                lowest_impedance = lowest_child_subtree_impedance.x[0]
                lowest_phase = lowest_child_subtree_impedance.x[1]
            }
        }
    }
    lowest_imp_vec = new Vector(2)
    lowest_imp_vec.x[0] = lowest_impedance
    lowest_imp_vec.x[1] = lowest_phase
    return lowest_imp_vec
}''')

# CableParams
CableParams = collections.namedtuple('CableParams',
                                     'length, diam, space_const,'
                                     'cm, rm, ra, e_leak, electrotonic_length')



# reduce_subtree as get_unique_cable_properties
def get_unique_cable_properties(subtree_root: h.Section, frequency: float) -> CableParams:
    '''Reduces the subtree  from the original_cell into one single section (cable).
    The reduction is done by finding the length and diameter of the cable (a
    single solution) that preserves the subtree's input impedance at the
    somatic end, and the transfer impedance in the subtree from the distal end
    to the proximal somatic end (between the new cable's two tips).
    '''

    subtree_root_ref = h.SectionRef(sec=subtree_root)
    cm, rm, ra, e_leak, q = _get_subtree_biophysical_properties(subtree_root_ref, frequency)

    # finds the subtree's input impedance (at the somatic-proximal end of the
    # subtree root section) and the lowest transfer impedance in the subtree in
    # relation to the somatic-proximal end (see more in Readme on NeuroReduce)
    imp_obj, root_input_impedance = measure_input_impedance_of_subtree(subtree_root, frequency)

    # in Ohms (a complex number)
    curr_lowest_subtree_imp = find_lowest_subtree_impedance(subtree_root_ref, imp_obj)

    # reducing the whole subtree into one section:
    # L = 1/q * arcosh(ZtreeIn(f)/min(ZtreeX,0(f)),
    # d = ( (2/pi * (sqrt(Rm*Ra)/q*ZtreeIn(f)) * coth(qL) )^(2/3) - from Gal Eliraz's thesis 1999
    new_cable_electrotonic_length = find_subtree_new_electrotonic_length(root_input_impedance,
                                                                         curr_lowest_subtree_imp,
                                                                         q)
    cable_electrotonic_length_as_complex = complex(new_cable_electrotonic_length, 0)
    new_cable_diameter_in_cm = _find_subtree_new_diam_in_cm(root_input_impedance,
                                                            cable_electrotonic_length_as_complex,
                                                            rm,
                                                            ra,
                                                            q)
    new_cable_diameter = new_cable_diameter_in_cm * 10000   # in microns

    # calculating the space constant, in order to find the cylinder's length:
    # space_const = sqrt(rm/(ri+r0))
    curr_space_const_in_cm = find_space_const_in_cm(new_cable_diameter_in_cm,
                                                    rm,
                                                    ra)
    curr_space_const_in_micron = 10000 * curr_space_const_in_cm
    new_cable_length = curr_space_const_in_micron * new_cable_electrotonic_length  # in microns

    return CableParams(length=new_cable_length,
                       diam=new_cable_diameter,
                       space_const=curr_space_const_in_micron,
                       cm=cm,
                       rm=rm,
                       ra=ra,
                       e_leak=e_leak,
                       electrotonic_length=new_cable_electrotonic_length)

def _get_subtree_biophysical_properties(subtree_root_ref, frequency):
    ''' gets the biophysical cable properties (Rm, Ra, Rc) and q
    for the subtree to be reduced according to the properties of the root section of the subtree
    '''
    section = subtree_root_ref.sec

    rm = 1.0 / section.gbar_Leak  # in ohm * cm^2
    # in secs, with conversion of the capacitance from uF/cm2 to F/cm2
    RC = rm * (float(section.cm) / 1000000)

    # defining q=sqrt(1+iwRC))
    angular_freq = 2 * math.pi * frequency   # = w
    q_imaginary = angular_freq * RC
    q = complex(1, q_imaginary)   # q=1+iwRC
    q = cmath.sqrt(q)		# q = sqrt(1+iwRC)

    return (section.cm,
            rm,
            section.Ra,  # in ohm * cm
            section.e_Leak,
            q)

def measure_input_impedance_of_subtree(subtree_root_section, frequency):
    '''measures the input impedance of the subtree with the given root section
    (at the "0" tip, the soma-proximal end),
    returns the Impedance hoc object and the input impedance as a complex value
    '''

    imp_obj = h.Impedance()
    CLOSE_TO_SOMA_EDGE = 0
    # sets origin for impedance calculations (soma-proximal end of root section)
    imp_obj.loc(CLOSE_TO_SOMA_EDGE, sec=subtree_root_section)

    # computes transfer impedance from every segment in the model in relation
    # to the origin location above
    imp_obj.compute(frequency + 1 / 9e9, 0)

    # in Ohms (impedance measured at soma-proximal end of root section)
    root_input_impedance = imp_obj.input(CLOSE_TO_SOMA_EDGE, sec=subtree_root_section) * 1000000
    root_input_phase = imp_obj.input_phase(CLOSE_TO_SOMA_EDGE, sec=subtree_root_section)
    # creates a complex impedance value out of the given polar coordinates
    root_input_impedance = cmath.rect(root_input_impedance, root_input_phase)
    return imp_obj, root_input_impedance

def find_lowest_subtree_impedance(subtree_root_ref, imp_obj):
    '''
    finds the segment in the subtree with the lowest transfer impedance in
    relation to the proximal-to-soma end of the given subtree root section,
    using a recursive hoc function,
    returns the lowest impedance in Ohms
    '''
    # returns [lowest subtree transfer impedance in Mohms, transfer phase]
    lowest_impedance = h.lowest_impedance_recursive(subtree_root_ref, imp_obj)
    # impedance saved as a complex number after converting Mohms to ohms
    curr_lowest_subtree_imp = cmath.rect(lowest_impedance.x[0] * 1000000, lowest_impedance.x[1])
    return curr_lowest_subtree_imp

# Length 
def find_subtree_new_electrotonic_length(root_input_impedance, lowest_subtree_impedance, q):
    ''' finds the subtree's reduced cable's electrotonic length
    based on the following equation:
    lowest_subtree_impedance = subtree_root_input_impedance/cosh(q*L)
    according to the given complex impedance values
    '''

    # this equation could be solved analytically using:
    # L = 1/q * arcosh(subtree_root_input_impedance/lowest_subtree_impedance),
    # But since L in this equation is complex number and we chose to focus on
    # finding the correct attenuation
    # we decided to search the L that will result with correct attenuation from
    # the tip of the dendrite to the soma.
    # We chose to use only real L (without a complex part)

    L = find_best_real_L(root_input_impedance, lowest_subtree_impedance, q)
    return L

def find_best_real_L(Z0, ZL_goal, q, max_L=10.0, max_depth=50):
    '''finds the best real L
    s.t. the modulus part of the impedance of ZL in eq 2.9 will be correct
    Since the modulus is a decreasing function of L, it is easy to find it using binary search.
    '''
    min_L = 0.0
    current_L = (min_L + max_L) / 2.0
    ZL_goal_A = cmath.polar(ZL_goal)[0]

    for _ in range(max_depth):
        Z_current_L_A = compute_zl_polar(Z0, current_L, q)[0]
        if abs(ZL_goal_A - Z_current_L_A) <= 0.001:  # Z are in Ohms , normal values are >10^6
            break
        elif ZL_goal_A > Z_current_L_A:
            current_L, max_L = (min_L + current_L) / 2.0, current_L
        else:
            current_L, min_L = (max_L + current_L) / 2.0, current_L
    else:
        logger.info("The difference between L and the goal L is larger than 0.001")
    return current_L

def compute_zl_polar(Z0, L, q):
    '''
    given Z0 , L and q computes the polar represntation of ZL (equation 2.9 in Gals thesis)
    '''
    ZL = Z0 * 1.0 / cmath.cosh(q * L)
    ZL = cmath.polar(ZL)
    return ZL

def compute_zx_polar(Z0, L, q, x):
    '''computes the polar represntation of Zx (equation 2.8 in Gals thesis)
    '''
    ZX = Z0 * cmath.cosh(q * (L - x)) / cmath.cosh(q * L)
    ZX = cmath.polar(ZX)
    return ZX

# Diam 
def _find_subtree_new_diam_in_cm(root_input_impedance, electrotonic_length_as_complex, rm, ra, q):
    '''finds the subtree's new cable's diameter (in cm)
    according to the given complex input impedance at the segment in the
    original subtree that is closest to the soma (the tip), and the given cable
    electrotonic length,
    with the following equation:
    d (in cm) = (2/PI * (sqrt(RM*RA)/(q*subtree_root_input_impedance)) *
                 (coth(q * NewCableElectrotonicLength)) )^(2/3)
    derived from Rall's cable theory for dendrites (Gal Eliraz)
    '''

    diam_in_cm = (2.0 / math.pi *
                  (math.sqrt(rm * ra) / (q * root_input_impedance)) *
                  (1 / cmath.tanh(q * electrotonic_length_as_complex))  # coth = 1/tanh
                  ) ** (2.0 / 3)

    '''
    # for debugging inaccuracies:
    if diam_in_cm.imag != 0:
        if abs(diam_in_cm.imag) > 0.03:
        print "PROBLEM - DIAM HAS SUBSTANTIAL IMAGINARY PART"
        print "\n"
    '''

    # the radius of the complex number received from the equation
    new_subtree_dend_diam_in_cm = cmath.polar(diam_in_cm)[0]
    return new_subtree_dend_diam_in_cm

# Space Const
def find_space_const_in_cm(diameter, rm, ra):
    ''' returns space constant (lambda) in cm, according to: space_const = sqrt(rm/(ri+r0)) '''
    # rm = Rm/(PI * diam), diam is in cm and Rm is in ohm * cm^2
    rm = float(rm) / (math.pi * diameter)
    # ri = 4*Ra/ (PI * diam^2), diam is in cm and Ra is in ohm * cm
    ri = float(4 * ra) / (math.pi * (diameter**2))
    space_const = math.sqrt(rm / ri)  # r0 is negligible
    return space_const


def apply_params_to_section(section: "Section", cable_params: CableParams, nseg: int):
    '''Apply new cable parameters to the given section in the model'''
    # Geometry
    section._ref.L = cable_params.length
    section._ref.diam = cable_params.diam
    # Segmentation
    section.nseg = nseg
    # Passive properties
    section._ref.cm = cable_params.cm
    section._ref.Ra = cable_params.ra
    section._ref.gbar_Leak = 1.0 / cable_params.rm
    section._ref.e_Leak = cable_params.e_leak
    