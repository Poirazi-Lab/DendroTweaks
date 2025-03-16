"""
This module contains functions for reducing dendritic subtrees into single cylinders.
The module incorporates code from neuron_reduce, which implements the algorithm described in:
Amsalem, O., Eyal, G., Rogozinski, N. et al. An efficient analytical reduction of detailed nonlinear neuron models. Nat Commun 11, 288 (2020). https://doi.org/10.1038/s41467-019-13932-6
The original code can be found at: https://github.com/orena1/neuron_reduce. Licensed under MIT License.
"""

import neuron
from neuron import h

import math
import cmath
import contextlib
import collections
import numpy as np
import logging

logger = logging.getLogger(__name__)


EXCLUDE_MECHANISMS = ['Leak', 'na_ion', 'k_ion', 'ca_ion', 'h_ion']

from dendrotweaks.morphology.reduce.reduced_cylinder import measure_input_impedance_of_subtree

@contextlib.contextmanager
def push_section(section):
    '''push a section onto the top of the NEURON stack, pop it when leaving the context'''
    section.push()
    yield
    h.pop_section()

def map_segs_to_params(root, mechanisms):
    segs_to_params = {}
    for sec in root.subtree:
        for seg in sec:
            segs_to_params[seg] = {}
            for mech_name, mech in mechanisms.items():
                if mech_name in EXCLUDE_MECHANISMS:
                    continue
                segs_to_params[seg][mech_name] = {}
                for param_name in mech.range_params_with_suffix:
                    segs_to_params[seg][mech_name][param_name] = seg.get_param_value(param_name)
    return segs_to_params


def map_segs_to_locs(root, reduction_frequency, new_cable_properties):
    """Maps segment names of the original subtree 
    to their new locations in the reduced cylinder.

    This dictionary is used later to restore 
    the active conductances in the reduced cylinder.
    """
    segs_to_locs = {}

    imp_obj, subtree_input_impedance = measure_input_impedance_of_subtree(root._ref,
                                                                        reduction_frequency)
    subtree_q = calculate_subtree_q(root._ref, reduction_frequency)

    for sec in root.subtree:
        for seg in sec:
            
            mid_of_segment_loc = reduce_segment(seg._ref,
                                                imp_obj,
                                                subtree_input_impedance,
                                                new_cable_properties.electrotonic_length,
                                                subtree_q)

            segs_to_locs[seg] = mid_of_segment_loc

    return segs_to_locs


def calculate_subtree_q(root, reduction_frequency):
    rm = 1.0 / root.gbar_Leak
    rc = rm * (float(root.cm) / 1000000)
    angular_freq = 2 * math.pi * reduction_frequency
    q_imaginary = angular_freq * rc
    q_subtree = complex(1, q_imaginary)   # q=1+iwRC
    q_subtree = cmath.sqrt(q_subtree)
    return q_subtree


def reduce_segment(seg,
                   imp_obj,
                   root_input_impedance,
                   new_cable_electrotonic_length,
                   subtree_q):

    # measures the original transfer impedance from the synapse to the
    # somatic-proximal end in the subtree root section
    sec = seg.sec

    with push_section(sec):
        orig_transfer_imp = imp_obj.transfer(seg.x) * 1000000  # ohms
        orig_transfer_phase = imp_obj.transfer_phase(seg.x)
        # creates a complex Impedance value with the given polar coordinates
        orig_transfer_impedance = cmath.rect(
            orig_transfer_imp, orig_transfer_phase)

    # synapse location could be calculated using:
    # X = L - (1/q) * arcosh( (Zx,0(f) / ZtreeIn(f)) * cosh(q*L) ),
    # derived from Rall's cable theory for dendrites (Gal Eliraz)
    # but we chose to find the X that will give the correct modulus. See comment about L values

    new_electrotonic_location = find_best_real_X(root_input_impedance,
                                                 orig_transfer_impedance,
                                                 subtree_q,
                                                 new_cable_electrotonic_length)
    new_relative_loc_in_section = (float(new_electrotonic_location) /
                                   new_cable_electrotonic_length)

    if new_relative_loc_in_section > 1:  # PATCH
        new_relative_loc_in_section = 0.999999

    return new_relative_loc_in_section


# find_best_real_X
def find_best_real_X(Z0, ZX_goal, q, L, max_depth=50):
    '''finds the best location of a synapse (X)
    s.t. the modulus part of the impedance of ZX in eq 2.8 will be correct.
    Since the modulus is a decreasing function of L, it is easy to find it using binary search.
    '''
    min_x, max_x = 0.0, L
    current_x = (min_x + max_x) / 2.0

    ZX_goal = cmath.polar(ZX_goal)[0]

    for _ in range(max_depth):
        Z_current_X_A = compute_zx_polar(Z0, L, q, current_x)[0]

        if abs(ZX_goal - Z_current_X_A) <= 0.001:
            break
        elif ZX_goal > Z_current_X_A:
            current_x, max_x = (min_x + current_x) / 2.0, current_x
        else:
            current_x, min_x = (max_x + current_x) / 2.0, current_x
    else:
        logger.info("The difference between X and the goal X is larger than 0.001")

    return current_x

def compute_zx_polar(Z0, L, q, x):
    '''computes the polar represntation of Zx (equation 2.8 in Gals thesis)
    '''
    ZX = Z0 * cmath.cosh(q * (L - x)) / cmath.cosh(q * L)
    ZX = cmath.polar(ZX)
    return ZX


def map_segs_to_reduced_segs(seg_to_locs, root):
    """Replaces the locations (x values) 
    with the corresponding segments of the reduced cylinder i.e. sec(x).
    """
    locs_to_reduced_segs = {loc: root(loc) 
        for loc in seg_to_locs.values()}
    segs_to_reduced_segs = {seg: locs_to_reduced_segs[loc] 
        for seg, loc in seg_to_locs.items()}
    return segs_to_reduced_segs


def map_reduced_segs_to_params(segs_to_reduced_segs, segs_to_params):
    reduced_segs_to_params = {}
    for seg, reduced_seg in segs_to_reduced_segs.items():
        if reduced_seg not in reduced_segs_to_params:
            reduced_segs_to_params[reduced_seg] = collections.defaultdict(list)
        for mech_name, mech_params in segs_to_params[seg].items():
            for param_name, param_value in mech_params.items():
                reduced_segs_to_params[reduced_seg][param_name].append(param_value)
    return reduced_segs_to_params


def set_avg_params_to_reduced_segs(reduced_segs_to_params):
    for reduced_seg, params in reduced_segs_to_params.items():
        for param_name, param_values in params.items():
            value = np.mean(param_values)
            reduced_seg.set_param_value(param_name, value)


def interpolate_missing_values(reduced_segs_to_params, root):

    non_mapped_segs = [seg for seg in root.segments 
        if seg not in reduced_segs_to_params]

    xs = np.array([seg.x for seg in root.segments])

    non_mapped_indices = np.where([seg in non_mapped_segs for seg in root.segments])[0]
    mapped_indices = np.where([seg not in non_mapped_segs for seg in root.segments])[0]

    print(f'Interpolated for ids {non_mapped_indices}')

    for param in list(set([k for val in reduced_segs_to_params.values() for k in val.keys()])):
        values = np.array([seg.get_param_value(param) for seg in root.segments])
        if np.any(values != 0.) and np.any(values == 0.):
            # Find the indices where param value is zero
            # zero_indices = np.where(values == 0)[0]
            # Interpolate the values for these indices
            # values[zero_indices] = np.interp(xs[zero_indices], xs[values != 0], values[values != 0], left=0, right=0)
            values[non_mapped_indices] = np.interp(xs[non_mapped_indices], xs[mapped_indices], values[mapped_indices], left=0, right=0)
            print(f'     {param} values: {values}')
            # Set the values
            for x, value in zip(xs, values):
                seg = root(x)
                seg.set_param_value(param, value)